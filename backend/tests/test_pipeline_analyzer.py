# tests/test_pipeline_analyzer.py

from app.models.pipeline import Pipeline, Node, Edge
from app.services.pipeline_analyzer import analyze_pipeline


def test_empty_pipeline():
    pipeline = Pipeline(nodes=[], edges=[])
    n, e, is_dag, cycle = analyze_pipeline(pipeline)

    assert n == 0
    assert e == 0
    assert is_dag is True
    assert cycle is None


def test_simple_dag():
    pipeline = Pipeline(
        nodes=[
            Node(id="a", type="input"),
            Node(id="b", type="output"),
        ],
        edges=[
            Edge(source="a", target="b"),
        ],
    )

    n, e, is_dag, cycle = analyze_pipeline(pipeline)

    assert n == 2
    assert e == 1
    assert is_dag is True
    assert cycle is None


def test_cycle_detection():
    pipeline = Pipeline(
        nodes=[
            Node(id="a", type="node"),
            Node(id="b", type="node"),
        ],
        edges=[
            Edge(source="a", target="b"),
            Edge(source="b", target="a"),
        ],
    )

    n, e, is_dag, cycle = analyze_pipeline(pipeline)

    assert is_dag is False
    assert cycle is not None
    assert cycle[0] == cycle[-1]
