from new_planet import *

class validate_input_test():
    def usual_case_test(s):
        assert validate_input("good_name45")

    def badchars_test(s):
        assert not validate_input("http://planeteria.org/ICannotFollowDirections")

    def spaces_test(s):
        assert not validate_input("planet name should not have spaces")

    def apostrophe_test(s):
        assert not validate_input("planet_name_shouldn't_have_an_apostrophe")
