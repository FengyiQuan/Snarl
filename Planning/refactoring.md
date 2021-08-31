# Milestone 6 - Refactoring Report

**Team members:** Shuhang Feng, Fengyi Quan

**Github team/repo:** https://github.ccs.neu.edu/CS4500-S21/Erenon/tree/master/Snarl


## Plan

List areas of your code/design you'd like to improve with brief descriptions,
anything that comes to mind. Tip: translate this list into Github Issues.

- create an abstract class to make `Room` and `Hallway` more clear
- build the common methods both for `Room` and `Hallway` for easier use
- pull out the mutation methods from `RuleChecker` to `GameState` to avoid copy mutation issue
- reconstruct the `ICharacter` to properly adapt `Player` and `Adversary`
- make all validity checker in `Level`, `Room` and `Hallway` work
- make python import package work as intended


## Changes

Summarize the work you have performed during this week.

- create `ITerrain` to abstract two classes and manage the helpful methods that share within both classes
- implement all common methods for both `Room` and `Hallway` and delete redundancy and repetition
- change methods from returning a new state to mutate the fields itself, moving all related code to `GameState`
- build a proper inheritance level of `ICharacter`, `Player` and `Adversary`
- double check the check methods and make all tests work as previous
- import root path every time when running single python file from command line tool
- integrate testStates to use the class we created this week, to be able to generate, as well as 
use the functions for those classes<br>


## Future Work

Summarize work you'd still like to do if there's time. This can include features 
you'd like to implement if given time.

We would really like to look for a python GUI, such as pyArcade<br>

## Conclusion

Any concluding remarks.
- refactoring is a huge step to advance code and make it more readable and understandable
