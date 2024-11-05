from lark import Lark, Tree, Token, UnexpectedToken
from pytest import mark
import pytest

grammar_path = "grammar/snakemake.lark"
LARK = Lark.open(grammar_path, parser="lalr", start="file_input")


@mark.parametrize(
    "snakefile",
    [
        # 1. Basic rule with single input and output
        """
    rule foo:
        input: "file1.txt"
        output: "output1.txt"
    """,
        # 2. Rule with multiple inputs and single output
        """
    rule bar:
        input: "file1.txt", "file2.txt"
        output: "output2.txt"
    """,
        # 3. Rule with multiple outputs
        """
    rule baz:
        input: "input.txt"
        output: "output1.txt"
    """,
        # 4. Rule with wildcard in input file
        """
    rule wildcard_example:
        input: "data/{sample}.txt"
        output: "results/{sample}.out"
    """,
        # 5. Rule with shell command
        """
    rule shell_example:
        input: "input.txt"
        output: "output.txt"
        shell: "cat {input} > {output}"
    """,
        # 6. Rule with params section
        """
    rule param_example:
        input: "file.txt"
        output: "output.txt"
        params: "value1"
    """,
        # 7. Rule with threads defined
        """
    rule thread_example:
        input: "input.txt"
        output: "output.txt"
        threads: 4
        shell: "cat {input} > {output}"
    """,
        # 8. Rule with resources
        """
    rule resource_example:
        input: "file.txt"
        output: "output.txt"
        resources: mem_mb=1024
    """,
        # 9. Rule with version specified
        """
    rule version_example:
        input: "file.txt"
        output: "output.txt"
        version: "1.0"
    """,
        # 10. Rule with conda environment
        """
    rule conda_example:
        input: "file.txt"
        output: "output.txt"
        conda: "env.yaml"
    """,
        # 11. Rule with log file
        """
    rule log_example:
        input: "file.txt"
        output: "output.txt"
        log: "logfile.log"
    """,
        # 12. Rule with multiple sections (input, output, params, log, shell)
        """
    rule complex_example:
        input: "file1.txt", "file2.txt"
        output: "output.txt"
        params: "-v"
        log: "log.txt"
        shell: "cat {input} > {output}"
    """,
        # 13. Rule with script section
        """
    rule script_example:
        input: "file.txt"
        output: "output.txt"
        script: "process_data.py"
    """,
        # 14. Rule with custom function in input
        """
    rule function_example:
        input: lambda wildcards: "data/{}.txt".format(wildcards.sample)
        output: "output.txt"
    """,
        # 15. Rule with priority
        """
    rule priority_example:
        input: "file.txt"
        output: "output.txt"
        priority: 100
    """,
        # 16. Rule with custom message
        """
    rule message_example:
        input: "file.txt"
        output: "output.txt"
        message: "Processing {input}"
    """,
        # 17. Rule with a temporary file
        """
    rule temp_example:
        input: "file.txt"
        output: temp("temp_output.txt")
    """,
        # 18. Rule with protected output file
        """
    rule protected_example:
        input: "file.txt"
        output: protected("protected_output.txt")
    """,
        # 19. Rule with dynamic output
        """
    rule dynamic_example:
        input: "file.txt"
        output: dynamic("output_{i}.txt")
    """,
        # 20. Rule with checkpoint
        # """
        # checkpoint checkpoint_example:
        #     input: "file.txt"
        #     output: "output.txt"
        #     shell: "cat {input} > {output}"
        # """
    ],
)
def test_parse_snakemake_file(snakefile):
    tree = lark.parse(snakefile)
    print(tree.pretty())


def test_parse_snakemake_param():
    snakefile = """
    rule foo:
        input: "file1.txt"
        output: "output1.txt"
    """
    tree = lark.parse(snakefile)
    print(tree.pretty())
    assert len(tree.children) == 1
    assert tree.children[0].data == "rule"
    assert len(tree.children[0].children) == 1
    assert tree.children[0].children[0].data == "rule_def"
    assert len(tree.children[0].children[0].children) == 3
    assert tree.children[0].children[0].children[0].data == "rule_header"
    assert tree.children[0].children[0].children[1].data == "rule_input"
    assert tree.children[0].children[0].children[2].data == "rule_output"

    rule_header = tree.children[0].children[0].children[0]
    assert rule_header.children[0].data == "rule_name"
    assert rule_header.children[0].children[0].value == "foo"

    rule_input = tree.children[0].children[0].children[1]
    assert rule_input.children[0].data == "input_files"
    assert len(rule_input.children[0].children) == 1
    assert rule_input.children[0].children[0].value == "file1.txt"

    rule_output = tree.children[0].children[0].children[2]
    assert rule_output.children[0].data == "output_files"
    assert len(rule_output.children[0].children) == 1
    assert rule_output.children[0].children[0].value == "output1.txt"


class TestPriority:
    def test_with_int(self):
        snakefile = """
        rule foo:
            priority: 50
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "50")])]

        assert subtree.children == expected

    def test_with_float(self):
        snakefile = """
        rule foo:
            priority: 50.0
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [Tree(Token("RULE", "number"), [Token("FLOAT_NUMBER", "50.0")])]

        assert subtree.children == expected

    def test_with_function_call(self):
        snakefile = """
        rule foo:
            priority: f()
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [
            Tree(
                "funccall",
                [
                    Tree("var", [Tree(Token("RULE", "name"), [Token("NAME", "f")])]),
                    None,
                ],
            )
        ]

        assert subtree.children == expected

    def test_with_variable(self):
        snakefile = """
        rule foo:
            priority: bar
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [Tree("var", [Tree(Token("RULE", "name"), [Token("NAME", "bar")])])]

        assert subtree.children == expected

    def test_with_arithmetic_expression(self):
        snakefile = """
        rule foo:
            priority: 50 + 50
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [
            Tree(
                Token("RULE", "arith_expr"),
                [
                    Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "50")]),
                    Token("PLUS", "+"),
                    Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "50")]),
                ],
            )
        ]

        assert subtree.children == expected

    def test_with_arithmetic_expression_with_workflow_cores_variable(self):
        snakefile = """
        rule foo:
            priority: 50 + workflow.cores
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [
            Tree(
                Token("RULE", "arith_expr"),
                [
                    Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "50")]),
                    Token("PLUS", "+"),
                    Tree(
                        "getattr",
                        [
                            Tree(
                                "var",
                                [
                                    Tree(
                                        Token("RULE", "name"),
                                        [Token("NAME", "workflow")],
                                    )
                                ],
                            ),
                            Tree(Token("RULE", "name"), [Token("NAME", "cores")]),
                        ],
                    ),
                ],
            )
        ]

        assert subtree.children == expected

    def test_with_getitem_expression(self):
        snakefile = """
        rule foo:
            priority: workflow["cores"]
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [
            Tree(
                "getitem",
                [
                    Tree(
                        "var",
                        [Tree(Token("RULE", "name"), [Token("NAME", "workflow")])],
                    ),
                    Tree(Token("RULE", "string"), [Token("STRING", '"cores"')]),
                ],
            )
        ]

        assert subtree.children == expected

    def test_with_inline_if_else(self):
        snakefile = """
        rule foo:
            priority: 50 if True else 100
        """
        tree = LARK.parse(snakefile)

        subtree = list(tree.find_data(Token("RULE", "priority")))[0]
        expected = [
            Tree(
                Token("RULE", "test"),
                [
                    Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "50")]),
                    Tree("const_true", []),
                    Tree(Token("RULE", "number"), [Token("DEC_NUMBER", "100")]),
                ],
            )
        ]

        assert subtree.children == expected

    def test_with_arithmetic_expression_with_string_fails(self):
        snakefile = """
        rule foo:
            priority: "50"
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)

    def test_with_arithmetic_expression_with_string_fails(self):
        snakefile = """
        rule foo:
            priority: "50" * 2
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)

    def test_with_lambda_fails(self):
        snakefile = """
        rule foo:
            priority: lambda: 50
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)

    def test_with_list_fails(self):
        snakefile = """
        rule foo:
            priority: [50]
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)

    def test_with_path_fails(self):
        snakefile = """
        rule foo:
            priority: DIR / "file.txt"
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)

    def test_with_assignment_fails(self):
        snakefile = """
        rule foo:
            priority: a = 50
        """
        with pytest.raises(UnexpectedToken):
            LARK.parse(snakefile)
