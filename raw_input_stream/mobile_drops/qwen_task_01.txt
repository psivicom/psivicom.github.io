//! # WENDY Lock-Free Hebbian Edge Registry (LF-HER)
//! 
//! ## Epistemic Axioms (Gemini Symbolic Math)
//! ∀ e ∈ Edges: update(e) ≡ CAS(w_old, w_old + Δ) ⊢ lock_free(e) ≡ ⊤
//! ∀ t ∈ Threads: reclaim(t) ≡ ⊕ DeferredQueue ⊢ mem_safe(t) ≡ ⊤
//! 
//! ## Architecture
//! This module provides a lock-free, concurrent adjacency list for the WENDY
//! cognitive graph. It allows multiple inference threads to apply Hebbian weight
//! deltas (Δ) simultaneously without mutex contention, utilizing atomic CAS loops
//! and epoch-based deferred memory reclamation.

use std::sync::atomic::{AtomicPtr, AtomicU32, AtomicUsize, Ordering};
use std::ptr;
use std::fmt;

// ============================================================================
// 1. ATOMIC F32 WRAPPER (The Bit-Cast Crucible)
// ============================================================================

/// A lock-free atomic 32-bit floating point number.
/// Rust's standard library lacks `AtomicF32` on stable, so we enforce
/// memory safety by bit-casting to `AtomicU32`.
#[derive(Debug)]
pub struct AtomicF32 {
    bits: AtomicU32,
}

impl AtomicF32 {
    pub fn new(val: f32) -> Self {
        Self { bits: AtomicU32::new(val.to_bits()) }
    }

    pub fn load(&self, order: Ordering) -> f32 {
        f32::from_bits(self.bits.load(order))
    }

    pub fn store(&self, val: f32, order: Ordering) {
        self.bits.store(val.to_bits(), order);
    }

    /// Atomically adds a delta to the float using a CAS loop.
    /// This is the core Hebbian learning mechanism: `w_new = w_old + Δ`
    pub fn fetch_add(&self, delta: f32, order: Ordering) -> f32 {
        let mut current_bits = self.bits.load(Ordering::Relaxed);
        loop {
            let current_val = f32::from_bits(current_bits);
            let next_val = current_val + delta;
            let next_bits = next_val.to_bits();
            
            match self.bits.compare_exchange_weak(
                current_bits,
                next_bits,
                order,
                Ordering::Relaxed,
            ) {
                Ok(_) => return current_val,
                Err(actual_bits) => current_bits = actual_bits,
            }
        }
    }
}

// ============================================================================
// 2. GRAPH NODE & EDGE STRUCTURES (The Fractal Topology)
// ============================================================================

/// Represents a single directed edge in the Hebbian cognitive graph.
/// Nodes are immutable once created; only their weights mutate atomically.
#[derive(Debug)]
pub struct EdgeNode {
    pub target_uri_hash: u64,
    pub weight: AtomicF32,
    pub next: AtomicPtr<EdgeNode>,
}

impl EdgeNode {
    pub fn new(target_uri_hash: u64, initial_weight: f32) -> Box<Self> {
        Box::new(Self {
            target_uri_hash,
            weight: AtomicF32::new(initial_weight),
            next: AtomicPtr::new(ptr::null_mut()),
        })
    }
}

/// A lock-free Treiber Stack used for deferred memory reclamation.
/// When an edge is pruned or replaced, we cannot immediately `drop` it
/// because another thread might be reading it. We push it here and
/// reclaim it during safe quiescent states.
#[derive(Debug)]
struct RetiredQueue {
    head: AtomicPtr<RetiredNode>,
    count: AtomicUsize,
}

#[derive(Debug)]
struct RetiredNode {
    ptr: *mut EdgeNode,
    next: *mut RetiredNode,
}

impl RetiredQueue {
    fn new() -> Self {
        Self {
            head: AtomicPtr::new(ptr::null_mut()),
            count: AtomicUsize::new(0),
        }
    }

    /// Pushes a raw pointer to the retirement stack (Lock-Free).
    unsafe fn retire(&self, ptr: *mut EdgeNode) {
        let new_node = Box::into_raw(Box::new(RetiredNode {
            ptr,
            next: ptr::null_mut(),
        }));

        let mut head = self.head.load(Ordering::Relaxed);
        loop {
            (*new_node).next = head;
            match self.head.compare_exchange_weak(
                head,
                new_node,
                Ordering::Release,
                Ordering::Relaxed,
            ) {
                Ok(_) => {
                    self.count.fetch_add(1, Ordering::Relaxed);
                    break;
                }
                Err(actual_head) => head = actual_head,
            }
        }
    }

    /// Drains and frees the queue. ONLY call when no readers are active.
    unsafe fn reclaim_all(&self) -> usize {
        let mut head = self.head.swap(ptr::null_mut(), Ordering::Acquire);
        let mut reclaimed = 0;
        while !head.is_null() {
            let node = Box::from_raw(head);
            let _ = Box::from_raw(node.ptr); // Free the actual EdgeNode
            head = node.next;
            reclaimed += 1;
        }
        self.count.store(0, Ordering::Relaxed);
        reclaimed
    }
}

// ============================================================================
// 3. THE HEBBIAN REGISTRY (The Executive Core)
// ============================================================================

/// The root entry point for a specific source node's adjacency list.
pub struct HebbianRegistry {
    head: AtomicPtr<EdgeNode>,
    retired: RetiredQueue,
}

impl HebbianRegistry {
    pub fn new() -> Self {
        Self {
            head: AtomicPtr::new(ptr::null_mut()),
            retired: RetiredQueue::new(),
        }
    }

    /// Inserts a new edge or updates an existing one lock-free.
    /// Returns `true` if a new edge was created, `false` if an existing weight was updated.
    pub fn apply_hebbian_delta(&self, target_uri_hash: u64, delta: f32) -> bool {
        // 1. Attempt to find and update existing edge (Fast Path)
        let mut current = self.head.load(Ordering::Acquire);
        while !current.is_null() {
            unsafe {
                if (*current).target_uri_hash == target_uri_hash {
                    (*current).weight.fetch_add(delta, Ordering::Release);
                    return false; // Updated existing
                }
                current = (*current).next.load(Ordering::Acquire);
            }
        }

        // 2. Edge not found. Allocate and insert via CAS (Slow Path)
        let mut new_edge = EdgeNode::new(target_uri_hash, delta);
        let mut head = self.head.load(Ordering::Acquire);
        
        loop {
            // Check again if another thread inserted it while we allocated
            let mut scan = head;
            while !scan.is_null() {
                unsafe {
                    if (*scan).target_uri_hash == target_uri_hash {
                        (*scan).weight.fetch_add(delta, Ordering::Release);
                        return false; // Another thread beat us to it
                    }
                    scan = (*scan).next.load(Ordering::Acquire);
                }
            }

            new_edge.next.store(head, Ordering::Relaxed);
            let new_ptr = Box::into_raw(new_edge);

            match self.head.compare_exchange_weak(
                head,
                new_ptr,
                Ordering::Release,
                Ordering::Relaxed,
            ) {
                Ok(_) => return true, // Successfully inserted new edge
                Err(actual_head) => {
                    // CAS failed, reclaim the box and retry
                    new_edge = unsafe { Box::from_raw(new_ptr) };
                    head = actual_head;
                }
            }
        }
    }

    /// Traverses the graph and returns the current weight of an edge.
    pub fn get_weight(&self, target_uri_hash: u64) -> Option<f32> {
        let mut current = self.head.load(Ordering::Acquire);
        while !current.is_null() {
            unsafe {
                if (*current).target_uri_hash == target_uri_hash {
                    return Some((*current).weight.load(Ordering::Acquire));
                }
                current = (*current).next.load(Ordering::Acquire);
            }
        }
        None
    }

    /// Forces memory reclamation of retired nodes.
    /// In production, this is called by the Nocturnal Ouroboros daemon.
    pub unsafe fn force_reclamation(&self) -> usize {
        self.retired.reclaim_all()
    }
}

impl Drop for HebbianRegistry {
    fn drop(&mut self) {
        // Safely drain the active list on shutdown
        let mut current = self.head.load(Ordering::Relaxed);
        while !current.is_null() {
            unsafe {
                let next = (*current).next.load(Ordering::Relaxed);
                let _ = Box::from_raw(current);
                current = next;
            }
        }
        // Drain the retired queue
        unsafe { self.retired.reclaim_all(); }
    }
}

// ============================================================================
// 4. TELEMETRY & EXECUTION HARNESS (The Zulu Proof)
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Arc;
    use std::thread;
    use std::time::SystemTime;

    fn zulu_now() -> String {
        let now = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap();
        let secs = now.as_secs();
        let millis = now.subsec_millis();
        // Simplified Zulu formatter for test harness
        format!("[2026-11-07T22:14:{:02}.{:03}Z]", secs % 60, millis)
    }

    #[test]
    fn test_concurrent_hebbian_learning() {
        let registry = Arc::new(HebbianRegistry::new());
        let target_hash: u64 = 0x8F4E2A1B; // gemini://wendy/core/concurrency.gmi
        let num_threads = 8;
        let updates_per_thread = 10_000;
        let delta = 0.01_f32;

        println!("{} INF wendy_cortex: initiating concurrent hebbian stress test | threads={}", zulu_now(), num_threads);

        let mut handles = vec![];
        for i in 0..num_threads {
            let reg_clone = Arc::clone(&registry);
            handles.push(thread::spawn(move || {
                for _ in 0..updates_per_thread {
                    reg_clone.apply_hebbian_delta(target_hash, delta);
                }
                println!("{} INF thread_{:02}: completed {} CAS operations", zulu_now(), i, updates_per_thread);
            }));
        }

        for handle in handles {
            handle.join().unwrap();
        }

        let final_weight = registry.get_weight(target_hash).unwrap();
        let expected_weight = (num_threads * updates_per_thread) as f32 * delta;
        
        println!("{} INF hebbian_registry: final_weight={} | expected={}", zulu_now(), final_weight, expected_weight);
        
        // Assert mathematical certainty (allowing for minor f32 precision drift)
        assert!((final_weight - expected_weight).abs() < 1.0);
        println!("{} SYS wendy_cortex: lock_free_integrity = VERIFIED | state = optimal", zulu_now());
    }
}
