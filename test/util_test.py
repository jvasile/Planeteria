# -*- coding: utf-8 -*-
import unittest
import util as u

bad_input = []
bad_input.extend([
# htmltidy rejects this first one because of the odd <section> tag at the end.
"""
<div><p>How you like me now?</p><section class="field">What up?</section></div>
""",
"<p>What about comments? <!-- comments! --> Do we like them?</p>",
])

class html_tidy_test(unittest.TestCase):
    "We shouldn't be using html_tidy anyway"
    def malformed_input_test(s):
        "Don't return a blank string on bad input."
        s.assertNotEqual(u.html_tidy(bad_input[0]), "")

class tidy2html_test(unittest.TestCase):

    def self_closing_tag_test(s):
        """Self-closing tags shouldn't be rendered as just <tag/>, except for <br/>.
        See bug # 10"""
        s.assertNotEqual(u.strip_body_tags(u.tidy2html("<i></i>")), '<i/>')

    def empty_tag_test(s):
        """Self-closing tags shouldn't be rendered as just <tag/>, except for <br/>.
        See bug # 10"""
        s.assertEqual(u.strip_body_tags(u.tidy2html("hey: <i> </i>")),
                    "<p>hey: <i> </i></p>")

    def odd_tag_test(s):
        "If the html has an odd tag (<section> in this case), don't puke or skip it"
        s.assertNotEqual(u.strip_body_tags(u.tidy2html(bad_input[0])), 
                         """<div>
<p>How you like me now?</p>
<section class="field">What up?</section>
</div>
""")

    def comment_test(s):
        "Don't panic if the html has a comment"
        s.assertEqual(u.strip_body_tags(u.tidy2html(bad_input[1])), 
                      "<p>What about comments? <!-- comments! --> Do we like them?</p>")

    def br_test_1(s):
        "Do we handle <br>?"
        a = u.strip_body_tags(u.tidy2html("<br>"))
        s.assertTrue(a == "<br/>" or a == "<br>")

    def br_test_2(s):
        "Do we handle <br/>?"
        a = u.strip_body_tags(u.tidy2html("<br/>"))
        s.assertTrue(a == "<br/>" or a == "<br>")

    def br_test_3(s):
        "Do we handle <br />?"
        a = u.strip_body_tags(u.tidy2html("<br />"))
        s.assertTrue(a == "<br/>" or a == "<br>")

    def br_test_4(s):
        "Do we handle <br></br>?"
        a = u.strip_body_tags(u.tidy2html("<br></br>"))
        s.assertTrue(a == "<br/>" or a == "<br>")


def main():
    print u.strip_body_tags(u.tidy2html(bad_input[0]))
if __name__ == "__main__":
    main()
