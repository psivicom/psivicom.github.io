use anyhow::{Result, bail};
use std::collections::HashMap;

#[derive(Debug, Clone, PartialEq)]
pub enum Symbol {
    Variable(String),
    Constant(f64),
    Operation(String, Box<Symbol>, Box<Symbol>),
    Proposition(String, Vec<Symbol>),
}

pub struct SymbolicEngine {
    axioms: HashMap<String, Symbol>,
}

impl SymbolicEngine {
    pub fn new() -> Result<Self> {
        let mut axioms = HashMap::new();
        axioms.insert("identity".to_string(), Symbol::Proposition("=".to_string(), vec![]));
        Ok(Self { axioms })
    }

    pub fn evaluate(&self, expr: &Symbol) -> Result<Symbol> {
        match expr {
            Symbol::Constant(c) => Ok(Symbol::Constant(*c)),
            Symbol::Variable(v) => bail!("Unbound variable in symbolic evaluation: {}", v),
            Symbol::Operation(op, left, right) => {
                let l = self.evaluate(left)?;
                let r = self.evaluate(right)?;
                
                if let (Symbol::Constant(lv), Symbol::Constant(rv)) = (l, r) {
                    match op.as_str() {
                        "+" => Ok(Symbol::Constant(lv + rv)),
                        "*" => Ok(Symbol::Constant(lv * rv)),
                        _ => bail!("Unsupported symbolic operation: {}", op),
                    }
                } else {
                    Ok(Symbol::Operation(op.clone(), Box::new(l), Box::new(r)))
                }
            }
            Symbol::Proposition(p, args) => Ok(Symbol::Proposition(p.clone(), args.clone())),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_constant_evaluation() {
        let engine = SymbolicEngine::new().unwrap();
        let expr = Symbol::Constant(42.0);
        let result = engine.evaluate(&expr).unwrap();
        assert_eq!(result, Symbol::Constant(42.0));
    }
}
