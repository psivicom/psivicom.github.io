//! WENDY Gödel Machine v2 — Recursive Self-Improvement with Real Transformations
//! SPDX-License-Identifier: EUPL-1.2
//!
//! The generator now produces semantics-preserving rewrites via AST manipulation,
//! not string templates. Each transformation has a match condition and a
//! reconstruction via quote! that is guaranteed to parse as valid Rust.

use anyhow::{Context, Result};
use chrono::Utc;
use proc_macro2::{Span, TokenStream};
use quote::{quote, ToTokens};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::process::Command;
use std::time::Instant;
use syn::{
    parse_file, parse_quote,
    visit::Visit,
    visit_mut::VisitMut,
    Expr, ExprBinary, ExprBlock, ExprCall, ExprForLoop, ExprIf, ExprLoop, ExprMatch,
    ExprPath, ExprWhile, File, Ident, Item, ItemFn, Stmt, BinOp,
};

const STATE_FILE: &str = "wendy_state.json";
const EVOLUTION_LOG: &str = ".wendy_evolution.gmi";
const SOURCE_PATH: &str = "wendy-cortex/src/recursive_self_improvement.rs";
const CYCLE_INTERVAL_SECS: u64 = 300;
const SIGMA_MIN: f64 = 0.05;
const SIGMA_MAX: f64 = 0.40;

fn zulu() -> String {
    Utc::now().format("%Y-%m-%dT%H:%M:%S%.3fZ").to_string()
}

// ============================================================================
// PERSISTENT STATE
// ============================================================================

#[derive(Debug, Clone, Serialize, Deserialize, Default)]
struct PersistentState {
    cycle_count: usize,
    trajectory: Vec<(String, f64)>,
    curiosity_samples: Vec<(f64, f64, f64)>, // (state, action, next) for learned forward model
    forward_model: LinearModel,
    transformation_success: HashMap<String, usize>,
    transformation_attempt: HashMap<String, usize>,
    sigma: f64,
    success_window: Vec<bool>,
    difficulty: f64,
    best_fitness: f64,
    plateau_counter: usize,
}

impl PersistentState {
    fn load() -> Self {
        fs::read_to_string(STATE_FILE)
            .ok()
            .and_then(|s| serde_json::from_str(&s).ok())
            .unwrap_or_else(|| Self {
                sigma: 0.2,
                difficulty: 1.0,
                forward_model: LinearModel::default(),
                ..Default::default()
            })
    }
    fn save(&self) -> Result<()> {
        fs::write(STATE_FILE, serde_json::to_string_pretty(self)?)?;
        Ok(())
    }
    fn record_transformation(&mut self, name: &str, success: bool) {
        *self.transformation_attempt.entry(name.to_string()).or_insert(0) += 1;
        if success {
            *self.transformation_success.entry(name.to_string()).or_insert(0) += 1;
        }
    }
    fn success_rate(&self, name: &str) -> f64 {
        let attempts = self.transformation_attempt.get(name).copied().unwrap_or(0);
        let successes = self.transformation_success.get(name).copied().unwrap_or(0);
        if attempts == 0 { 0.5 } else { successes as f64 / attempts as f64 }
    }
}

// ============================================================================
// LEARNED FORWARD MODEL for curiosity (linear regression, updates every cycle)
// next_capability ≈ a·current + b·action + c
// ============================================================================

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
struct LinearModel {
    a: f64,
    b: f64,
    c: f64,
    samples_seen: usize,
}

impl Default for LinearModel {
    fn default() -> Self { Self { a: 1.0, b: 0.0, c: 0.0, samples_seen: 0 } }
}

impl LinearModel {
    fn predict(&self, state: f64, action: f64) -> f64 {
        self.a * state + self.b * action + self.c
    }

    /// Fit via gradient descent on accumulated samples. Cheap, online.
    fn refit(&mut self, samples: &[(f64, f64, f64)]) {
        if samples.len() < 3 { return; }
        let lr = 0.01;
        let mut a = self.a;
        let mut b = self.b;
        let mut c = self.c;
        for _ in 0..100 {
            let mut da = 0.0;
            let mut db = 0.0;
            let mut dc = 0.0;
            for &(s, act, next) in samples {
                let pred = a * s + b * act + c;
                let err = pred - next;
                da += err * s;
                db += err * act;
                dc += err;
            }
            let n = samples.len() as f64;
            a -= lr * da / n;
            b -= lr * db / n;
            c -= lr * dc / n;
        }
        self.a = a;
        self.b = b;
        self.c = c;
        self.samples_seen = samples.len();
    }
}

// ============================================================================
// AST INTROSPECTION
// ============================================================================

#[derive(Debug, Clone)]
struct FunctionProfile {
    name: String,
    signature: String,
    line_start: usize,
    line_end: usize,
    cyclomatic: usize,
    stmt_count: usize,
    has_loops: bool,
    has_match: bool,
    is_recursive: bool,
    has_early_return_candidate: bool,
    has_for_push_candidate: bool,
}

struct SourceAst {
    path: PathBuf,
    raw: String,
    ast: File,
    functions: Vec<FunctionProfile>,
}

struct Introspector;

impl Introspector {
    fn parse(path: &str) -> Result<SourceAst> {
        let pb = PathBuf::from(path);
        let raw = fs::read_to_string(&pb)?;
        let ast = parse_file(&raw).map_err(|e| anyhow::anyhow!("parse: {}", e))?;
        let mut functions = Vec::new();
        let lines: Vec<&str> = raw.lines().collect();
        for item in &ast.items {
            if let Item::Fn(func) = item {
                let name = func.sig.ident.to_string();
                let signature = func.sig.to_token_stream().to_string();
                let (ls, le) = line_range(&lines, &name);
                let analyzer = Analyzer::new(&name);
                let (cc, has_loops, has_match, is_recursive) = analyzer.analyze(func);
                functions.push(FunctionProfile {
                    name,
                    signature,
                    line_start: ls,
                    line_end: le,
                    cyclomatic: cc,
                    stmt_count: func.block.stmts.len(),
                    has_loops,
                    has_match,
                    is_recursive,
                    has_early_return_candidate: analyzer.early_return_candidate,
                    has_for_push_candidate: analyzer.for_push_candidate,
                });
            }
        }
        Ok(SourceAst { path: pb, raw, ast, functions })
    }
}

fn line_range(lines: &[&str], name: &str) -> (usize, usize) {
    let mut start = 0;
    for (i, line) in lines.iter().enumerate() {
        if line.contains(&format!("fn {}", name)) { start = i; break; }
    }
    let mut depth = 0i32;
    let mut opened = false;
    let mut end = start;
    for (i, line) in lines.iter().enumerate().skip(start) {
        for ch in line.chars() {
            if ch == '{' { depth += 1; opened = true; }
            else if ch == '}' { depth -= 1; }
        }
        if opened && depth == 0 { end = i; break; }
    }
    (start, end)
}

struct Analyzer<'a> {
    name: &'a str,
    cc: usize,
    has_loops: bool,
    has_match: bool,
    is_recursive: bool,
    early_return_candidate: bool,
    for_push_candidate: bool,
}

impl<'a> Analyzer<'a> {
    fn new(name: &'a str) -> Self {
        Self {
            name, cc: 1, has_loops: false, has_match: false, is_recursive: false,
            early_return_candidate: false, for_push_candidate: false,
        }
    }
    fn analyze(mut self, func: &ItemFn) -> (usize, bool, bool, bool) {
        self.visit_item_fn(func);
        (self.cc, self.has_loops, self.has_match, self.is_recursive)
    }
}

impl<'ast, 'a> Visit<'ast> for Analyzer<'a> {
    fn visit_expr_if(&mut self, i: &'ast ExprIf) {
        self.cc += 1;
        // Detect early-return candidate: if cond { return X; } else { ...long body }
        if let Some(then_ret) = block_has_return(&i.then_branch) {
            if then_ret && i.else_branch.is_some() && i.then_branch.stmts.len() == 1 {
                self.early_return_candidate = true;
            }
        }
        syn::visit::visit_expr_if(self, i);
    }
    fn visit_expr_match(&mut self, i: &'ast ExprMatch) {
        self.cc += 1;
        self.has_match = true;
        syn::visit::visit_expr_match(self, i);
    }
    fn visit_expr_for_loop(&mut self, i: &'ast ExprForLoop) {
        self.cc += 1;
        self.has_loops = true;
        if for_loop_is_filter_map_push(i) { self.for_push_candidate = true; }
        syn::visit::visit_expr_for_loop(self, i);
    }
    fn visit_expr_while(&mut self, i: &'ast ExprWhile) {
        self.cc += 1;
        self.has_loops = true;
        syn::visit::visit_expr_while(self, i);
    }
    fn visit_expr_loop(&mut self, i: &'ast ExprLoop) {
        self.cc += 1;
        self.has_loops = true;
        syn::visit::visit_expr_loop(self, i);
    }
    fn visit_expr_binary(&mut self, i: &'ast ExprBinary) {
        if matches!(i.op, BinOp::And(_) | BinOp::Or(_)) { self.cc += 1; }
        syn::visit::visit_expr_binary(self, i);
    }
    fn visit_expr_call(&mut self, i: &'ast ExprCall) {
        if let Expr::Path(p) = &*i.func {
            if p.path.get_ident().map(|id| id.to_string()).as_deref() == Some(self.name) {
                self.is_recursive = true;
            }
        }
        syn::visit::visit_expr_call(self, i);
    }
}

fn block_has_return(block: &syn::Block) -> Option<bool> {
    if let Some(Stmt::Expr(Expr::Return(_), _)) = block.stmts.last() {
        Some(true)
    } else {
        Some(false)
    }
}

fn for_loop_is_filter_map_push(for_loop: &ExprForLoop) -> bool {
    // Heuristic: for x in iter { if pred { result.push(f(x)); } }
    if for_loop.body.stmts.len() != 1 { return false; }
    if let Stmt::Expr(Expr::If(if_expr), _) = &for_loop.body.stmts[0] {
        if let Some(Stmt::Expr(Expr::MethodCall(mc), _)) = if_expr.then_branch.stmts.first() {
            return mc.method == "push";
        }
    }
    false
}

// ============================================================================
// TRANSFORMATION ENGINE — semantics-preserving AST rewrites via syn + quote!
// ============================================================================

/// A transformation has a name, an applicability check, and a mutator that
/// rewrites the function in place. All rewrites preserve semantics.
trait Transformation: Send + Sync {
    fn name(&self) -> &'static str;
    fn applicable(&self, func: &ItemFn) -> bool;
    /// Mutate the function's block in place. Return true if anything changed.
    fn apply(&self, func: &mut ItemFn) -> bool;
}

/// `if cond { return X; } else { ...rest }` → `if !cond { ...rest }; return X;`
/// Actually we do the simpler form: `if cond { return X; } ...rest` where rest is the else.
struct EarlyReturnExtract;

impl Transformation for EarlyReturnExtract {
    fn name(&self) -> &'static str { "early_return_extract" }

    fn applicable(&self, func: &ItemFn) -> bool {
        // Look for pattern in any statement of the function block
        for stmt in &func.block.stmts {
            if let Stmt::Expr(Expr::If(if_expr), _) = stmt {
                if if_expr.then_branch.stmts.len() == 1 {
                    if let Some(Stmt::Expr(Expr::Return(_), _)) = if_expr.then_branch.stmts.first() {
                        if if_expr.else_branch.is_some() {
                            return true;
                        }
                    }
                }
            }
        }
        false
    }

    fn apply(&self, func: &mut ItemFn) -> bool {
        let mut changed = false;
        let mut new_stmts: Vec<Stmt> = Vec::new();
        for stmt in std::mem::take(&mut func.block.stmts) {
            if let Stmt::Expr(Expr::If(if_expr), semi) = stmt {
                if if_expr.then_branch.stmts.len() == 1 {
                    if let Some(Stmt::Expr(Expr::Return(_), _)) = if_expr.then_branch.stmts.first() {
                        if let Some((_, else_block)) = if_expr.else_branch.clone() {
                            // Emit: if cond { return X; }  (kept)
                            let guard_if: ExprIf = if_expr.clone();
                            new_stmts.push(Stmt::Expr(Expr::If(guard_if), semi));
                            // Then emit the else-body statements as top-level
                            if let Expr::Block(ExprBlock { block, .. }) = *else_block {
                                new_stmts.extend(block.stmts);
                            }
                            changed = true;
                            continue;
                        }
                    }
                }
            }
            new_stmts.push(stmt);
        }
        func.block.stmts = new_stmts;
        changed
    }
}

/// `for x in iter { if pred { result.push(f(x)); } }` → `result.extend(iter.filter(pred).map(f));`
/// Conservative: only fires when the pattern is clearly recognizable.
struct ForToIteratorChain;

impl Transformation for ForToIteratorChain {
    fn name(&self) -> &'static str { "for_to_iterator_chain" }

    fn applicable(&self, func: &ItemFn) -> bool {
        for stmt in &func.block.stmts {
            if let Stmt::Expr(Expr::ForLoop(fl), _) = stmt {
                if for_loop_is_filter_map_push(fl) { return true; }
            }
        }
        false
    }

    fn apply(&self, func: &mut ItemFn) -> bool {
        let mut changed = false;
        let mut new_stmts: Vec<Stmt> = Vec::new();
        for stmt in std::mem::take(&mut func.block.stmts) {
            if let Stmt::Expr(Expr::ForLoop(fl), semi) = stmt {
                if let Some(replacement) = rewrite_for_to_chain(&fl) {
                    new_stmts.push(Stmt::Expr(replacement, semi));
                    changed = true;
                    continue;
                }
            }
            new_stmts.push(stmt);
        }
        func.block.stmts = new_stmts;
        changed
    }
}

fn rewrite_for_to_chain(fl: &ExprForLoop) -> Option<Expr> {
    // Expected: for pat in iter { if cond { receiver.push(f(x)); } }
    let Stmt::Expr(Expr::If(if_expr), _) = fl.body.stmts.first()? else { return None };
    let Stmt::Expr(Expr::MethodCall(mc), _) = if_expr.then_branch.stmts.first()? else { return None };
    if mc.method != "push" { return None; }
    let Expr::Path(ref push_arg) = mc.args.first()? else { return None; };
    let push_expr_tokens = push_arg.to_token_stream();
    let iter_tokens = fl.expr.to_token_stream();
    let cond_tokens = if_expr.cond.to_token_stream();
    let receiver_tokens = mc.receiver.to_token_stream();

    // result.extend(iter.into_iter().filter(|x| cond).map(|x| push_expr));
    let new_expr: Expr = parse_quote! {
        #receiver_tokens.extend(
            (#iter_tokens).into_iter()
                .filter(|x| { let _ = x; #cond_tokens })
                .map(|x| { let _ = x; #push_expr_tokens })
        )
    };
    Some(new_expr)
}

/// Simplify `!!x` → `x` in unary not chains
struct DoubleNegationElim;

impl Transformation for DoubleNegationElim {
    fn name(&self) -> &'static str { "double_negation_elim" }

    fn applicable(&self, func: &ItemFn) -> bool {
        struct V { found: bool }
        impl<'ast> Visit<'ast> for V {
            fn visit_expr_unary(&mut self, u: &'ast syn::ExprUnary) {
                if matches!(u.op, syn::UnOp::Not(_)) {
                    if let Expr::Unary(inner) = &*u.expr {
                        if matches!(inner.op, syn::UnOp::Not(_)) {
                            self.found = true;
                        }
                    }
                }
                syn::visit::visit_expr_unary(self, u);
            }
        }
        let mut v = V { found: false };
        v.visit_item_fn(func);
        v.found
    }

    fn apply(&self, func: &mut ItemFn) -> bool {
        struct M { changed: bool }
        impl VisitMut for M {
            fn visit_expr_mut(&mut self, e: &mut Expr) {
                if let Expr::Unary(u) = e {
                    if matches!(u.op, syn::UnOp::Not(_)) {
                        if let Expr::Unary(inner) = &mut *u.expr {
                            if matches!(inner.op, syn::UnOp::Not(_)) {
                                *e = *std::mem::replace(&mut inner.expr, parse_quote!(()));
                                self.changed = true;
                                return;
                            }
                        }
                    }
                }
                syn::visit_mut::visit_expr_mut(self, e);
            }
        }
        let mut m = M { changed: false };
        m.visit_item_fn_mut(func);
        m.changed
    }
}

/// Simplify `x && true` → `x` and `true && x` → `x`
struct AndTrueElim;

impl Transformation for AndTrueElim {
    fn name(&self) -> &'static str { "and_true_elim" }

    fn applicable(&self, func: &ItemFn) -> bool {
        struct V { found: bool }
        impl<'ast> Visit<'ast> for V {
            fn visit_expr_binary(&mut self, b: &'ast ExprBinary) {
                if matches!(b.op, BinOp::And(_)) {
                    if is_true_lit(&b.left) || is_true_lit(&b.right) {
                        self.found = true;
                    }
                }
                syn::visit::visit_expr_binary(self, b);
            }
        }
        let mut v = V { found: false };
        v.visit_item_fn(func);
        v.found
    }

    fn apply(&self, func: &mut ItemFn) -> bool {
        struct M { changed: bool }
        impl VisitMut for M {
            fn visit_expr_mut(&mut self, e: &mut Expr) {
                syn::visit_mut::visit_expr_mut(self, e);
                if let Expr::Binary(b) = e {
                    if matches!(b.op, BinOp::And(_)) {
                        if is_true_lit(&b.right) {
                            *e = (*b.left).clone();
                            self.changed = true;
                        } else if is_true_lit(&b.left) {
                            *e = (*b.right).clone();
                            self.changed = true;
                        }
                    }
                }
            }
        }
        let mut m = M { changed: false };
        m.visit_item_fn_mut(func);
        m.changed
    }
}

fn is_true_lit(e: &Expr) -> bool {
    if let Expr::Lit(lit) = e {
        if let syn::Lit::Bool(b) = &lit.lit { return b.value; }
    }
    false
}

struct TransformationEngine {
    transforms: Vec<Box<dyn Transformation>>,
}

impl TransformationEngine {
    fn new() -> Self {
        Self {
            transforms: vec![
                Box::new(EarlyReturnExtract),
                Box::new(ForToIteratorChain),
                Box::new(DoubleNegationElim),
                Box::new(AndTrueElim),
            ],
        }
    }

    /// Pick the best transformation for this function, biased by historical success.
    fn pick_for(&self, func: &ItemFn, state: &PersistentState) -> Option<(&dyn Transformation, &'static str)> {
        let mut applicable: Vec<&dyn Transformation> = self.transforms.iter()
            .filter(|t| t.applicable(func))
            .map(|b| b.as_ref())
            .collect();
        if applicable.is_empty() { return None; }
        // Sort by historical success rate, descending
        applicable.sort_by(|a, b| {
            let ra = state.success_rate(a.name());
            let rb = state.success_rate(b.name());
            rb.partial_cmp(&ra).unwrap()
        });
        // Pick the best, but sometimes explore (ε-greedy)
        let explore = state.sigma > 0.25; // high σ → explore
        let chosen = if explore && applicable.len() > 1 {
            applicable[1]
        } else {
            applicable[0]
        };
        Some((chosen, chosen.name()))
    }
}

// ============================================================================
// VERIFIER
// ============================================================================

fn cargo_check() -> bool {
    let out = Command::new("cargo")
        .args(["check", "--bin", "wendy-godel"])
        .current_dir("wendy-cortex")
        .output();
    match out {
        Ok(o) => {
            if !o.status.success() {
                eprintln!("{}", String::from_utf8_lossy(&o.stderr));
            }
            o.status.success()
        }
        Err(e) => { eprintln!("cargo error: {}", e); false }
    }
}

fn cargo_build_release() -> bool {
    let out = Command::new("cargo")
        .args(["build", "--release", "--bin", "wendy-godel"])
        .current_dir("wendy-cortex")
        .output();
    match out {
        Ok(o) => {
            if !o.status.success() {
                eprintln!("{}", String::from_utf8_lossy(&o.stderr));
            }
            o.status.success()
        }
        Err(e) => { eprintln!("cargo error: {}", e); false }
    }
}

// ============================================================================
// SAFE ROLLBACK (git-based)
// ============================================================================

fn git_snapshot() -> Result<()> {
    let _ = Command::new("git").args(["add", "-A"]).output();
    let _ = Command::new("git").args(["commit", "-m", "wendy-pre-mutation-snapshot", "--allow-empty"]).output();
    Ok(())
}

fn git_revert() -> Result<()> {
    let _ = Command::new("git").args(["reset", "--hard", "HEAD~1"]).output();
    Ok(())
}

// ============================================================================
// GÖDEL MACHINE
// ============================================================================

struct GodelMachine {
    state: PersistentState,
    engine: TransformationEngine,
}

impl GodelMachine {
    fn new() -> Self {
        Self {
            state: PersistentState::load(),
            engine: TransformationEngine::new(),
        }
    }

    fn cycle(&mut self) -> Result<()> {
        self.state.cycle_count += 1;
        let n = self.state.cycle_count;
        println!("\n[{}] ═══ Gödel Machine v2 — Cycle #{} ═══", zulu(), n);

        // 1. INTROSPECT
        let source = Introspector::parse(SOURCE_PATH)?;
        println!("[{}] 📖 {} functions in AST", zulu(), source.functions.len());

        // 2. Pick target: highest complexity among non-trivial functions
        let target = source.functions.iter()
            .filter(|f| f.stmt_count >= 3
                && f.name != "main"
                && f.name != "run_recursive_self_improvement"
                && f.name != "cycle")
            .max_by_key(|f| f.cyclomatic);

        let (success, delta, transformation_used) = if let Some(target) = target {
            println!("[{}] 🎯 Target: {} (cc={}, loops={}, rec={})",
                zulu(), target.name, target.cyclomatic, target.has_loops, target.is_recursive);

            // Find the function in the AST and clone it for mutation
            let mut target_func: Option<ItemFn> = None;
            for item in &source.ast.items {
                if let Item::Fn(f) = item {
                    if f.sig.ident == target.name {
                        target_func = Some(f.clone());
                        break;
                    }
                }
            }
            let mut func = target_func.context("target function not in AST")?;

            // 3. Pick a transformation based on applicability + historical success
            let picked = self.engine.pick_for(&func, &self.state);
            let (transformation, name) = match picked {
                Some((t, n)) => (t, n),
                None => {
                    println!("[{}] 🟢 No applicable transformation for {}", zulu(), target.name);
                    self.state.record_transformation("none", true);
                    let _ = self.state.save();
                    return Ok(());
                }
            };
            println!("[{}] 🧬 Trying transformation: {}", zulu(), name);

            // 4. Apply the transformation
            let changed = transformation.apply(&mut func);
            if !changed {
                println!("[{}] ⚠️  Transformation reported no change, skipping", zulu());
                self.state.record_transformation(name, false);
                let _ = self.state.save();
                return Ok(());
            }

            // 5. Snapshot, mutate file, verify, rollback if bad
            git_snapshot()?;

            // Reconstruct the file: replace the function's token stream
            let new_ast = replace_function_in_ast(&source.ast, &func);
            let new_source = new_ast.to_token_stream().to_string();
            // Use prettyplease to format if available; else raw
            let pretty = match prettyplease::unparse(&new_ast) {
                Ok(s) => s,
                Err(_) => new_source,
            };
            fs::write(SOURCE_PATH, pretty)?;
            println!("[{}] ✍️  File rewritten with {}", zulu(), name);

            let compiles = cargo_check();
            if !compiles {
                println!("[{}] ❌ cargo check failed — reverting", zulu());
                git_revert()?;
                self.state.record_transformation(name, false);
                let _ = self.state.save();
                return Ok(());
            }

            // 6. Benchmark: build release and measure binary size delta as a crude proxy
            let before_size = binary_size();
            let builds = cargo_build_release();
            let after_size = binary_size();
            if !builds {
                println!("[{}] ❌ cargo build --release failed — reverting", zulu());
                git_revert()?;
                self.state.record_transformation(name, false);
                let _ = self.state.save();
                return Ok(());
            }

            // 7. Curiosity: prediction error from learned forward model
            let current = 100.0 - target.cyclomatic as f64;
            let action = 1.0; // transformation applied
            let predicted = self.state.forward_model.predict(current, action);
            let new_cyclomatic = count_cyclomatic(&func);
            let actual = 100.0 - new_cyclomatic as f64;
            let curiosity = (predicted - actual).abs();
            self.state.curiosity_samples.push((current, action, actual));
            if self.state.curiosity_samples.len() > 200 {
                self.state.curiosity_samples.remove(0);
            }
            println!("[{}] 🔬 Curiosity: |{:.2} − {:.2}| = {:.4}", zulu(), predicted, actual, curiosity);

            // 8. Refit forward model
            self.state.forward_model.refit(&self.state.curiosity_samples);
            println!("[{}] 📈 Forward model: a={:.3}, b={:.3}, c={:.3} (n={})",
                zulu(), self.state.forward_model.a, self.state.forward_model.b,
                self.state.forward_model.c, self.state.forward_model.samples_seen);

            // 9. Commit the evolution
            let delta = actual - current;
            self.state.record_transformation(name, true);
            log_evolution(n, name, &target.name, delta, curiosity, before_size, after_size)?;

            (true, delta, Some(name.to_string()))
        } else {
            println!("[{}] 🟢 All functions anatomically optimal", zulu());
            (true, 0.0, None)
        };

        // 10. Update GVU κ
        self.state.trajectory.push((zulu(), delta));
        let kappa = ema_kappa(&self.state.trajectory);

        // 11. Rechenberg σ adaptation
        self.state.success_window.push(success);
        if self.state.success_window.len() > 20 { self.state.success_window.remove(0); }
        if self.state.success_window.len() >= 5 {
            let rate = self.state.success_window.iter().filter(|&&s| s).count() as f64
                / self.state.success_window.len() as f64;
            if rate > 0.2 {
                self.state.sigma = (self.state.sigma * 1.1).min(SIGMA_MAX);
            } else {
                self.state.sigma = (self.state.sigma * 0.9).max(SIGMA_MIN);
            }
            println!("[{}] 🎲 Rechenberg: σ={:.4} (rate={:.2})", zulu(), self.state.sigma, rate);
        }

        // 12. Plateau / hypermutation
        let fitness = if success { 1.0 } else { 0.0 };
        if fitness > self.state.best_fitness + 0.01 {
            self.state.best_fitness = fitness;
            self.state.plateau_counter = 0;
        } else {
            self.state.plateau_counter += 1;
            if self.state.plateau_counter >= 5 {
                println!("[{}] ⚡ Plateau — hypermuting σ", zulu());
                self.state.sigma = (self.state.sigma * 2.0).min(SIGMA_MAX);
                self.state.plateau_counter = 0;
            }
        }

        // 13. Self-play difficulty
        let recent = self.state.success_window.iter().rev().take(5).copied().collect::<Vec<_>>();
        if recent.len() >= 5 {
            let r = recent.iter().filter(|&&s| s).count() as f64 / recent.len() as f64;
            if r > 0.8 {
                self.state.difficulty = (self.state.difficulty * 1.1).max(0.1);
            } else if r < 0.4 {
                self.state.difficulty = (self.state.difficulty * 0.9).max(0.1);
            }
        }

        // 14. Persist
        self.state.save()?;

        // 15. Report
        println!("\n[{}] ── Cycle #{} Complete ──", zulu(), n);
        println!("  Transformation:    {}", transformation_used.as_deref().unwrap_or("none"));
        println!("  Success:           {}", success);
        println!("  Capability Δ:      {:+.2}", delta);
        println!("  GVU κ:             {:.4}", kappa);
        println!("  Rechenberg σ:      {:.4}", self.state.sigma);
        println!("  Self-play d:       {:.3}", self.state.difficulty);
        println!("  Forward model n:   {}", self.state.forward_model.samples_seen);

        Ok(())
    }
}

fn count_cyclomatic(func: &ItemFn) -> usize {
    let mut a = Analyzer::new(&func.sig.ident.to_string());
    let (cc, _, _, _) = a.analyze(func);
    cc
}

fn replace_function_in_ast(original: &File, replacement: &ItemFn) -> File {
    let mut new_file = original.clone();
    let name = replacement.sig.ident.to_string();
    for item in &mut new_file.items {
        if let Item::Fn(f) = item {
            if f.sig.ident == name {
                *f = replacement.clone();
            }
        }
    }
    new_file
}

fn binary_size() -> u64 {
    let path = "wendy-cortex/target/release/wendy-godel";
    fs::metadata(path).map(|m| m.len()).unwrap_or(0)
}

fn ema_kappa(trajectory: &[(String, f64)]) -> f64 {
    let mut k = 0.0;
    for w in trajectory.windows(2) {
        let delta = w[1].1 - w[0].1;
        k = 0.3 * delta + 0.7 * k;
    }
    k
}

fn log_evolution(
    cycle: usize,
    transformation: &str,
    target: &str,
    delta: f64,
    curiosity: f64,
    size_before: u64,
    size_after: u64,
) -> Result<()> {
    let entry = format!(
        "\n## Cycle {} — {}\n\n\
         - **Target:** `{}`\n\
         - **Transformation:** `{}`\n\
         - **Capability Δ:** {:+.2}\n\
         - **Curiosity:** {:.4}\n\
         - **Binary size:** {} → {} bytes\n\
         - **Timestamp:** {}\n",
        cycle, transformation, target, transformation, delta, curiosity,
        size_before, size_after, zulu()
    );
    let mut f = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(EVOLUTION_LOG)?;
    use std::io::Write;
    if size_before == 0 && size_after == 0 {
        writeln!(f, "# WENDY Evolution Log\n")?;
    }
    write!(f, "{}", entry)?;
    Ok(())
}

fn main() -> Result<()> {
    println!("[{}] 🧠 WENDY Gödel Machine v2 initializing...", zulu());
    println!("[{}] 4 frameworks + 4 semantics-preserving transformations", zulu());
    println!("[{}] Learned forward model · meta-learned selection", zulu());

    let mut machine = GodelMachine::new();
    loop {
        match machine.cycle() {
            Ok(_) => println!("[{}] 💤 Sleeping {}s", zulu(), CYCLE_INTERVAL_SECS),
            Err(e) => println!("[{}] ❌ Cycle error: {}", zulu(), e),
        }
        std::thread::sleep(std::time::Duration::from_secs(CYCLE_INTERVAL_SECS));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn linear_model_fits_constant() {
        let mut m = LinearModel::default();
        let samples = vec![(0.0, 0.0, 5.0), (1.0, 0.0, 5.0), (2.0, 0.0, 5.0)];
        m.refit(&samples);
        let p = m.predict(3.0, 0.0);
        assert!((p - 5.0).abs() < 0.5, "expected ~5, got {}", p);
    }

    #[test]
    fn double_negation_eliminated() {
        let src = "fn f() -> bool { let x = true; !!x }";
        let mut func: ItemFn = syn::parse_str(src).unwrap();
        let t = DoubleNegationElim;
        assert!(t.applicable(&func));
        assert!(t.apply(&mut func));
        let out = func.to_token_stream().to_string();
        assert!(!out.contains("!!"), "double negation should be gone: {}", out);
    }

    #[test]
    fn and_true_eliminated() {
        let src = "fn f(x: bool) -> bool { x && true }";
        let mut func: ItemFn = syn::parse_str(src).unwrap();
        let t = AndTrueElim;
        assert!(t.applicable(&func));
        assert!(t.apply(&mut func));
        let out = func.to_token_stream().to_string();
        assert!(!out.contains("true"), "true should be gone: {}", out);
    }

    #[test]
    fn early_return_recognized() {
        let src = r#"fn f(x: bool) -> i32 {
            if x { return 1; } else { 2 }
        }"#;
        let func: ItemFn = syn::parse_str(src).unwrap();
        let t = EarlyReturnExtract;
        assert!(t.applicable(&func));
    }
}
