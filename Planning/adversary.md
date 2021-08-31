### Adversary
<<<<<<< HEAD
For Adversary, it is the sub abstract class inherited from ICharacter.

It inherited all methods and fields from ICharacter:

fields: some fields maybe a fixed value by certain type of adversary
- name, turn, move_range, position, move_restrict, seen_range

methods: 
All methods from abstract class. It does not contain the methods related to `is_alive` filed since no adversary should
be dead. Besides, it has a methods get_type to get the exact type of this adversary. It would be a helper function to 
indicate the type. Probably, it can be done by type dispatch. (using instance, for example)
