# From Principia Mathematica to Lean: How a Century of Logic Led to Machine-Checked Mathematics

## Why try to mechanise mathematics? The questions that frame the story

Interactive theorem proving means an arrangement where a machine and a human user work together to produce a formal proof[1].
At one extreme, the computer acts merely as a checker on a detailed formal proof produced by a human; at the other, the prover is highly automated while still subject to some degree of human guidance[1].
Automated theorem proving aims to prove assertions fully automatically, without human guidance[1].

Automath was the first interactive system to use the Curry-Howard isomorphism to encode proofs[1].
The LCF tradition later turned each primitive inference rule into an ML function returning an object of type thm[1].
Later sections link these episodes to the design of today's proof assistants.

## Logicism and Russell's paradox: why Principia needed types

Logicism is the view that some or all of mathematics can be reduced to formal logic, usually stated as a two-part thesis: all mathematical truths can be translated into logical truths, and all mathematical proofs can be recast as logical proofs[2].
Naive set theory lets any coherent condition determine a set: for any propositional function $P(x)$ with $x$ as a free variable, there exists a set whose members are exactly the things with property $P$[3].

Let $R$ be the set of all sets that are not members of themselves, and ask whether $R \in R$[3].
If $R \in R$, then by definition $R$ must not be a member of itself; if $R \notin R$, then by definition $R$ must be a member of itself[3].
The set of all teacups is not a member of itself, while the set of all non-teacups is a member of itself[3].
Burali-Forti had found a similar antinomy in 1897 about the set of ordinals, but Russell's paradox relies only on the primitive notion of set[3].
Because classical logic lets all sentences follow from a contradiction, many worried that no mathematical proof could be trusted if set theory was inconsistent[3].

Russell's response was a theory of types, which arranges sentences into a hierarchy, with sentences about individuals at the bottom and sentences about sets of individuals above them[3].
The theory is motivated in large part by the vicious circle principle, which holds that no propositional function can be defined prior to specifying the function's scope of application[3].
The cost was high: the axiom of reducibility was introduced to overcome the not completely satisfactory effects of the type restriction, and many critics judged it too ad hoc[2].
As an analogy only, the hierarchy works like a type checker that rejects any expression applying a value to itself.
Principia Mathematica, by Whitehead and Russell, appeared in three volumes in 1910, 1912 and 1913 as a defence of logicism, and it served as a major impetus for research in the foundations of mathematics throughout the twentieth century[2].

## Hilbert's programme: formalise everything and prove it consistent by finitary means

Formalising mathematics axiomatically means setting up a system of axioms and accepting as correct only those statements that can be derived from them by a finite number of logical steps[4].
Hilbert's programme, put forward in the early 1920s, asked for this formalisation of all of mathematics together with a proof that the axiomatisation is consistent[5].
A system is inconsistent if there is some statement A such that both A and ¬A are provable from the axioms[4].
Consistency mattered because a contradiction discovered by Zermelo and Russell had a catastrophic effect on mathematics[4].

Hilbert separated finitary reasoning, which works with concrete signs surveyable in all their parts, from the ideal elements of classical mathematics[5].
The programme's goal was a finitary consistency proof of the formal system, showing that no formal derivation of a formula A and of its negation exists[5].
The companion hope was the Entscheidungsproblem, the search for a general mechanical process that decides whether a given formula is provable[4].

Goals and outcomes must be kept apart.
Gödel's work is generally taken to show that the programme cannot be carried out as originally conceived[5].
His second incompleteness theorem shows that a system such as Principia cannot prove its own consistency[5].
Turing and Church showed that the Entscheidungsproblem has no solution[4].
The sources report debate over whether the first or the second incompleteness theorem delivered the decisive blow, though those most directly involved judged that the theorems had a decisive impact[5].
After about 1934 it was almost universally accepted that the methods accepted as finitary before Gödel's results are formalisable in PA[5].

Relativised programmes continue the idea: Gentzen published a consistency proof of first-order Peano Arithmetic in 1936, using transfinite induction up to epsilon-zero[5].
Reverse mathematics, developed by Friedman and Simpson, asks how much classical mathematics can be reduced to finitary mathematics, for instance showing that the Hahn-Banach theorem is provable in $WKL_0$[5].

## Gödel's incompleteness theorems: what formal systems cannot do

Gödel's two incompleteness theorems concern the limits of provability in formal axiomatic theories[6].
A formal system is a set of axioms with rules of inference whose axioms and proof relation are decidable, so a finite sequence of formulas can be mechanically checked as a proof[6].
The first theorem, in Rosser's improved form, says that any consistent formal system F in which a certain amount of elementary arithmetic can be carried out has statements that it can neither prove nor disprove[6].
The second says that such a system cannot prove its own consistency[6].

The proof rests on coding: the symbols, formulas and proofs of F are each assigned a natural number, and the Gödel number of a formula A is written ⌈A⌉[6].
Because this coding is effective, syntactic operations become arithmetical functions, so neg(⌈A⌉) = ⌈¬A⌉[6].
In any consistent system containing Q, Robinson arithmetic, the strongly representable sets are exactly the recursive ones, where a recursive set is one that a mechanical procedure can decide[6].
The formula Prov_F(x) expresses that x is provable in F, and it is weakly representable[6].

Because formulas are numbers, a formula can be built that talks about its own code, which is the idea of self-reference[6].
The diagonalization lemma mechanically constructs, for any formula A(x) with one free variable, a self-referential sentence D with F ⊢ D ↔ A(⌈D⌉)[6].
Applied to the negated provability predicate, the lemma yields the Gödel sentence G_F, which satisfies F ⊢ G_F ↔ ¬Prov_F(⌈G_F⌉)[6].
In informal explanations G_F is often said to say of itself that it is not provable, but such statements should be taken with a grain of salt[6].
If F proved G_F, it would prove ¬G_F, so F would be inconsistent; hence, if F is consistent, G_F is unprovable[6].

Gödel's theorems pose, at least prima facie, serious problems for Hilbert's program[6].
Incompleteness concerns derivability in a particular system, not truth in an absolute sense[6].
It does not say that proofs cannot be checked mechanically, since the proof relation is decidable[6].
A proof assistant such as Lean checks proofs inside one fixed formal system, and no consistent system containing arithmetic proves every statement of its language[6].

## Decidability: Church, Turing and the limits of mechanical procedure

The Entscheidungsproblem asks whether there is a general mechanical procedure that decides, for any formula, whether it is provable in a calculus[4].
An effective method is a procedure set out in finitely many exact instructions that produces its result in finitely many steps and demands no insight, intuition or ingenuity from the person carrying it out[4].
A theory is decidable when its set of theorems is recursive, and by the Church-Turing thesis this is the same as there being a mechanical procedure that decides whether an arbitrary sentence is a theorem[6].

Church identified effective calculability with recursiveness or with lambda-definability, meaning expressibility in Church's lambda-calculus, a notation for functions and their application, while Turing analysed human computation in terms of machines[4].
Both showed the Entscheidungsproblem for the functional calculus unsolvable, and Turing stated that the Hilbert Entscheidungsproblem can have no solution[4].

Church's diagonal argument runs by contradiction from an effective enumeration $A_1, A_2, \ldots$ of the formulas that have a normal form, meaning formulas containing no part that lambda-conversion can still reduce[7].
Church then defines $E(n)$ to differ from $A_n(n)$ on the diagonal, so $E$ cannot be on the list, yet $E$ is effectively calculable and so would have to appear on it, a contradiction[7].
Gödel's tools also give undecidability: any consistent theory containing Robinson arithmetic Q is undecidable[6].

The proven result is that the Entscheidungsproblem has no solution relative to the formalised notions of recursiveness, lambda-definability and Turing computability, which coincide[4].
The Church-Turing thesis is different: it claims that these formal notions capture every effective method, and it is a thesis rather than a theorem[4].
Turing held that his arguments for the thesis are fundamentally appeals to intuition, and he described its status as something between a theorem and a definition[4].

Turing noted that he saw no essential difference between a proof-checking machine and a proof-finding machine[4].
Checking a given proof is therefore a mechanical task, whereas finding a proof of an arbitrary provable formula has no general procedure, which is why proof assistants rely on human guidance.

## Type theory and the Curry-Howard correspondence: proofs as programs

Section 5 asked what a machine can decide about provability, and this section asks how a proof can itself be a program that a machine checks.
Propositions as Types has three levels: each proposition corresponds to a type, each proof to a program of that type, and each simplification of a proof to an evaluation of a program[8].
Gentzen's natural deduction gives each connective an introduction rule, which says how to assert it, and an elimination rule, which says how to use it[8].
Church's simply-typed lambda calculus ruled out self-application, a step similar to Russell's solution with types[8, 2].

The lambda calculus has only three constructs: variables, function abstraction and function application[8].
Here $\lambda x.N$ is the function with parameter $x$ and body $N$, and $M\,N$ applies a function $M$ to an argument $N$[8].
The judgment $M : A$ says that term $M$ has type $A$, where $A \times B$ is the product type and $A \to B$ the function type[8].

Conjunction $A \wedge B$ corresponds to the product type $A \times B$, and a proof of $A \wedge B$ consists of a proof of $A$ and a proof of $B$[8].
Implication $A \supset B$ corresponds to the function type $A \to B$, so a proof of $A \supset B$ turns a proof of $A$ into a proof of $B$[8].
Abstracting over a variable $z$ of type $B \times A$ gives $\lambda z.\langle \pi_2 z, \pi_1 z\rangle : (B \times A) \to (A \times B)$, which reads as a proof of $(B \wedge A) \supset (A \wedge B)$ and as a program that swaps the components of a pair[8].
Simplifying a proof corresponds to evaluating a program: a redex $(\lambda x.N)\,M$ is rewritten to the reduct $N[M/x]$, and rewrites preserve types[8].

Because each typing rule matches a proof rule, checking that a term has a given type is checking that the term is a proof of the corresponding proposition, so proof checking becomes type checking[8].
Dependent types let a type depend on a value, and Howard proposed that the quantifiers $\forall$ and $\exists$ correspond to such types[8].
The precise isomorphism is established for the fragments the source treats, such as simply typed lambda calculus and intuitionistic natural deduction[8].
The wider claim that the principle unifies logic, computation and other fields is the author's framing rather than a theorem[8].
The Church-Turing limits discussed earlier still apply to what a type checker can decide in general.

## From Automath to Coq to Lean: how proof assistants grew out of these ideas

A proof assistant needs a small program that every proof must pass through before it is accepted, and this program is called the kernel[9].
The authors say that Lean has a relatively small trusted kernel, and that its rich API allows users to export their developments to other systems and implement their own reference checkers[9].
Tactics and automation are implemented in Lean itself, and users can modify and extend them[9].

De Bruijn's Automath, conceived in the second half of the 1960s, was the earliest proof checker, designed so that a computer could check the correctness of a formalised text[10].
Its central insight was that types in a typed lambda calculus can be regarded as proof classes, with the elements of a type as proofs of a proposition[10].
A formalisation of Landau's Grundlagen der Analysis, about 500 pages of Automath text, was verified in October 1975 by a program only a few pages long[10].
The Automath project had a direct influence on the Calculus of Constructions, which became the basis of the proof assistant Coq[10].

In the LCF approach, the primitive inference rules are the only constructors of an abstract type thm, which Milner introduced so that a guarantee holds that theorems were created by the primitive rules[1].
Coq was extended in the LCF style with tactics that operate on goals, in version 4.10 in 1989[1].
Mizar, by contrast, keeps a batch-oriented style where proof scripts are checked in their entirety per run[1].

Lean 4 is a reimplementation of the Lean theorem prover in Lean itself, which the authors say addresses many shortcomings of the previous versions[9].
It is both an extensible theorem prover and an efficient programming language, and its code generator produces C code, so users can write proof automation in Lean and load it as a plugin[9].
Users can modify and extend the parser, elaborator, tactics, decision procedures, pretty printer and code generator, and the system has a hygienic macro system custom-built for interactive theorem provers[9].

## Case study: the Four Colour Theorem checked in Coq

The Four Colour Theorem was first conjectured in 1852, and Appel and Haken proved it in 1976 with computer programs that carried out a case analysis too large to perform by hand[11].
Gonthier wrote a formal proof script covering both the mathematical and computational parts, and the Coq proof checker mechanically verified it[11].

The key idea is computation inside the logic: in Coq, P(2 + 2) and P(4) are identical, so a proof of one serves as a proof of the other, which is called computational reflection[11].
The lemma check_reducible_valid says that if the boolean program check_reducible returns true then the proposition cfreducible holds, so a large case analysis is discharged by running a verified program[11].

The rest of the stack is also trusted: the processor, its operating system, the Coq proof checker, and the OCaml compiler, but none of these is specific to the theorem, since they are off-the-shelf and tested on many other jobs[11].
The report demonstrates that a proof combining mathematics and large computation can be fully checked[11].
It does not show that proof assistants are generally easy to use.

## Side by side: the main approaches compared

The table below compares the main approaches by the problem each addressed, the limitation it fixed, what it established, and its remaining cost.

- Principia Mathematica (ramified type theory): addressed reducing mathematics to logic; restricted well-formed expressions by a theory of types, the mechanism used to avoid Russell's paradox; cost: many critics judged the axiom of reducibility too ad hoc[2].
- Hilbert's finitary formalism: addressed securing mathematics by formalisation and a finitary consistency proof; established only a programme, not a result; cost: Gödel's second theorem blocks a finitary consistency proof of Principia[5].
- Gödel's incompleteness theorems: addressed the limits of provability in consistent arithmetical systems; established that such systems have undecided sentences and cannot prove their own consistency; cost: the limit applies to every such system[6].
- Church's lambda-calculus and Turing machines: addressed the lack of a precise notion of effective procedure; established that the Entscheidungsproblem has no solution, while equating the formal notions with effectiveness is a thesis; cost: the general case of the Entscheidungsproblem is unsolvable[4].
- Curry-Howard type theory: addressed the gap between proof systems and computation; established a precise correspondence between propositions and types and between proofs and programs; cost: the correspondence applies to a range of logics[8].
- Automath: addressed mechanical checking of whole mathematical texts; established the earliest proof checker, which checks syntactic correctness with one fixed algorithm (a design choice)[10].
- Coq: addressed interactive proof on a type-theoretic foundation; established tactics that operate on goals in the LCF style, a design choice[1].
- Lean 4: addressed shortcomings of earlier Lean versions; established a reimplementation that is both prover and programming language, in the authors' description[9].

Incompleteness and undecidability are fundamental limits, since they hold for any system of the stated kind[6, 4].
Usability and automation are engineering limits[1].

## Summary and self-check questions

This tutorial asked whether all mathematical truth can be derived by rules, whether those rules can be shown consistent, and whether a machine can check the result.
Russell's paradox forced types, and Principia Mathematica answered it with a hierarchy of types[2].
Gödel's second theorem says that for any consistent system F within which a certain amount of elementary arithmetic can be carried out, the consistency of F cannot be proved in F itself[6].
Church and Turing showed the Entscheidungsproblem unsolvable relative to their formal notions, and the claim that these capture every effective method is a thesis, not a theorem[4].
For each proof of a proposition there is a program of the corresponding type, and vice versa[8].
The Four Colour proof in Coq leaves the reader to check the short statement of the theorem and its definitions, while the remaining 60,000 lines are checked by Coq[11].

- Why does Russell's paradox motivate types?
- What did Gödel's second theorem refute in Hilbert's programme?
- Why is proof checking decidable while theoremhood is not?
- What does the Curry-Howard correspondence identify, and why does it make a type checker a proof checker?
- Why is the Church-Turing thesis a thesis rather than a theorem?
- What does Gonthier's Four Colour proof show about trust?

## References

1. cl.cam.ac.uk (2015). [*History of Interactive Theorem Proving*](https://www.cl.cam.ac.uk/~jrh13/papers/joerg.pdf). cl.cam.ac.uk (scholarly).
2. Irvine, A. D. (1996). [*Principia Mathematica*](https://plato.stanford.edu/archives/fall2014/entries/principia-mathematica). plato.stanford.edu (scholarly).
3. Irvine, A. D. (n.d.). [*Russell's Paradox*](https://plato.stanford.edu/archives/sum2009/entries/russell-paradox). plato.stanford.edu (scholarly).
4. plato.stanford.edu (n.d.). [*The Church-Turing Thesis > The Rise and Fall of the Entscheidungsproblem (Stanford Encyclopedia of Philosophy)*](https://plato.stanford.edu/entries/church-turing/decision-problem.html). plato.stanford.edu (reference).
5. Zach, R. (2003). [*Hilbert’s Program*](https://plato.stanford.edu/entries/hilbert-program). plato.stanford.edu (scholarly).
6. Raatikainen, P. (2013). [*Gödel's Incompleteness Theorems*](https://plato.stanford.edu/archives/spr2017/entries/goedel-incompleteness). plato.stanford.edu (scholarly).
7. plato.stanford.edu (n.d.). [*Alonzo Church > A. Computability and the Church-Turing Thesis (Stanford Encyclopedia of Philosophy)*](https://plato.stanford.edu/entries/church/supplementA.html). plato.stanford.edu (scholarly).
8. homepages.inf.ed.ac.uk (2015). [*Propositions as Types*](https://homepages.inf.ed.ac.uk/wadler/papers/propositions-as-types/propositions-as-types.pdf). homepages.inf.ed.ac.uk (institutional).
9. lean-lang.org (2021). [*The Lean 4 Theorem Prover and Programming Language*](https://lean-lang.org/papers/lean4.pdf). lean-lang.org (official).
10. scispace.com (n.d.). [*N.G. de Bruijn (1918–2012) and his Road to Automath ...*](https://scispace.com/pdf/n-g-de-bruijn-1918-2012-and-his-road-to-automath-the-23qe1iqaug.pdf). scispace.com (scholarly).
11. cse.chalmers.se (2005). [*A computer-checked proof of the Four Colour Theorem*](https://www.cse.chalmers.se/~abela/lehre/WS05-06/CAFR/4colproof.pdf). cse.chalmers.se (institutional).
