namespace Optimization

structure Problem where
  center : Int
  lower : Int

def Feasible (p : Problem) (x : Int) : Prop :=
  p.lower ≤ x

def objective (p : Problem) (x : Int) : Int :=
  (x - p.center) * (x - p.center)

def Stationary (p : Problem) (x : Int) : Prop :=
  x = p.center

structure KKTPoint (p : Problem) (x : Int) where
  primal_feasible : Feasible p x
  multiplier : Int
  dual_feasible : 0 ≤ multiplier
  stationarity : Stationary p x
  complementary_slackness :
    multiplier * (x - p.lower) = 0

lemma sq_nonnegative (a : Int) :
    0 ≤ a * a := by
  omega

lemma objective_nonnegative (p : Problem) (x : Int) :
    0 ≤ objective p x := by
  unfold objective
  exact sq_nonnegative (x - p.center)

lemma stationary_objective_zero
    (p : Problem) (x : Int)
    (hs : Stationary p x) :
    objective p x = 0 := by
  unfold Stationary at hs
  subst x
  simp [objective]

lemma stationary_global_minimum
    (p : Problem) (x y : Int)
    (hx : Stationary p x)
    (hy : Feasible p y) :
    objective p x ≤ objective p y := by
  have hnonneg : 0 ≤ objective p y :=
    objective_nonnegative p y

  have hxzero : objective p x = 0 :=
    stationary_objective_zero p x hx

  omega

theorem kkt_global_optimality
    (p : Problem) (x : Int)
    (hkkt : KKTPoint p x) :
    ∀ y : Int,
      Feasible p y →
        objective p x ≤ objective p y := by
  intro y hy

  exact stationary_global_minimum
    p x y
    hkkt.stationarity
    hy

theorem kkt_objective_uniqueness
    (p : Problem) (x y : Int)
    (hx : KKTPoint p x)
    (hy : KKTPoint p y) :
    objective p x = objective p y := by
  have hxy :
      objective p x ≤ objective p y :=
    kkt_global_optimality p x hx y hy.primal_feasible

  have hyx :
      objective p y ≤ objective p x :=
    kkt_global_optimality p y hy x hx.primal_feasible

  omega

end Optimization
