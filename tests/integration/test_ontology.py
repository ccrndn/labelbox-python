from typing import Any, Dict, List, Union

import pytest

from labelbox import LabelingFrontend
from labelbox.exceptions import InconsistentOntologyException
from labelbox.schema.ontology import Tool, Classification, Option, \
    Ontology, OntologyBuilder

_SAMPLE_ONTOLOGY = {
    "tools": [{
        "schemaNodeId": None,
        "featureSchemaId": None,
        "required": False,
        "name": "poly",
        "color": "#FF0000",
        "tool": "polygon",
        "classifications": []
    }, {
        "schemaNodeId": None,
        "featureSchemaId": None,
        "required": False,
        "name": "segment",
        "color": "#FF0000",
        "tool": "superpixel",
        "classifications": []
    }, {
        "schemaNodeId":
            None,
        "featureSchemaId":
            None,
        "required":
            False,
        "name":
            "bbox",
        "color":
            "#FF0000",
        "tool":
            "rectangle",
        "classifications": [{
            "schemaNodeId":
                None,
            "featureSchemaId":
                None,
            "required":
                True,
            "instructions":
                "nested classification",
            "name":
                "nested classification",
            "type":
                "radio",
            "options": [{
                "schemaNodeId":
                    None,
                "featureSchemaId":
                    None,
                "label":
                    "first",
                "value":
                    "first",
                "options": [{
                    "schemaNodeId": None,
                    "featureSchemaId": None,
                    "required": False,
                    "instructions": "nested nested text",
                    "name": "nested nested text",
                    "type": "text",
                    "options": []
                }]
            }, {
                "schemaNodeId": None,
                "featureSchemaId": None,
                "label": "second",
                "value": "second",
                "options": []
            }]
        }, {
            "schemaNodeId": None,
            "featureSchemaId": None,
            "required": True,
            "instructions": "nested text",
            "name": "nested text",
            "type": "text",
            "options": []
        }]
    }, {
        "schemaNodeId": None,
        "featureSchemaId": None,
        "required": False,
        "name": "dot",
        "color": "#FF0000",
        "tool": "point",
        "classifications": []
    }, {
        "schemaNodeId": None,
        "featureSchemaId": None,
        "required": False,
        "name": "polyline",
        "color": "#FF0000",
        "tool": "line",
        "classifications": []
    }, {
        "schemaNodeId": None,
        "featureSchemaId": None,
        "required": False,
        "name": "ner",
        "color": "#FF0000",
        "tool": "named-entity",
        "classifications": []
    }],
    "classifications": [{
        "schemaNodeId":
            None,
        "featureSchemaId":
            None,
        "required":
            True,
        "instructions":
            "This is a question.",
        "name":
            "This is a question.",
        "type":
            "radio",
        "options": [{
            "schemaNodeId": None,
            "featureSchemaId": None,
            "label": "yes",
            "value": "yes",
            "options": []
        }, {
            "schemaNodeId": None,
            "featureSchemaId": None,
            "label": "no",
            "value": "no",
            "options": []
        }]
    }]
}


@pytest.mark.parametrize("tool_type", list(Tool.Type))
def test_create_tool(tool_type) -> None:
    t = Tool(tool=tool_type, name="tool")
    assert (t.tool == tool_type)


@pytest.mark.parametrize("class_type", list(Classification.Type))
def test_create_classification(class_type) -> None:
    c = Classification(class_type=class_type, instructions="classification")
    assert (c.class_type == class_type)


@pytest.mark.parametrize("value, expected_value, typing",
                         [(3, 3, int), ("string", "string", str)])
def test_create_option(value, expected_value, typing) -> None:
    o = Option(value=value)
    assert (o.value == expected_value)
    assert (o.value == o.label)


def test_create_empty_ontology() -> None:
    o = OntologyBuilder()
    assert (o.tools == [])
    assert (o.classifications == [])


def test_add_ontology_tool() -> None:
    o = OntologyBuilder()
    o.add_tool(Tool(tool=Tool.Type.BBOX, name="bounding box"))

    second_tool = Tool(tool=Tool.Type.SEGMENTATION, name="segmentation")
    o.add_tool(second_tool)
    assert len(o.tools) == 2

    for tool in o.tools:
        assert (type(tool) == Tool)

    with pytest.raises(InconsistentOntologyException) as exc:
        o.add_tool(Tool(tool=Tool.Type.BBOX, name="bounding box"))
    assert "Duplicate tool name" in str(exc.value)


def test_add_ontology_classification() -> None:
    o = OntologyBuilder()
    o.add_classification(
        Classification(class_type=Classification.Type.TEXT,
                       instructions="text"))

    second_classification = Classification(
        class_type=Classification.Type.CHECKLIST, instructions="checklist")
    o.add_classification(second_classification)
    assert len(o.classifications) == 2

    for classification in o.classifications:
        assert (type(classification) == Classification)

    with pytest.raises(InconsistentOntologyException) as exc:
        o.add_classification(
            Classification(class_type=Classification.Type.TEXT,
                           instructions="text"))
    assert "Duplicate classification instructions" in str(exc.value)


def test_tool_add_classification() -> None:
    t = Tool(tool=Tool.Type.SEGMENTATION, name="segmentation")
    c = Classification(class_type=Classification.Type.TEXT, instructions="text")
    t.add_classification(c)
    assert t.classifications == [c]

    with pytest.raises(Exception) as exc:
        t.add_classification(c)
    assert "Duplicate nested classification" in str(exc)


def test_classification_add_option() -> None:
    c = Classification(class_type=Classification.Type.RADIO,
                       instructions="radio")
    o = Option(value="option")
    c.add_option(o)
    assert c.options == [o]

    with pytest.raises(InconsistentOntologyException) as exc:
        c.add_option(Option(value="option"))
    assert "Duplicate option" in str(exc.value)


def test_option_add_option() -> None:
    o = Option(value="option")
    c = Classification(class_type=Classification.Type.TEXT, instructions="text")
    o.add_option(c)
    assert o.options == [c]

    with pytest.raises(InconsistentOntologyException) as exc:
        o.add_option(c)
    assert "Duplicate nested classification" in str(exc.value)


def test_ontology_asdict(project) -> None:
    assert OntologyBuilder.from_dict(
        _SAMPLE_ONTOLOGY).asdict() == _SAMPLE_ONTOLOGY


def test_from_project_ontology(client, project) -> None:
    o = OntologyBuilder.from_project(project)
    assert o.asdict() == project.ontology().normalized
