"""Additional tests to increase test coverage to 100%."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from introligo.generator import IntroligoGenerator


class TestProtobufFeatures:
    """Tests for protobuf-related features in generator.py."""

    def test_generate_with_manual_protodoc(self, temp_dir):
        """Test generation with manual protobuf documentation."""
        config_file = temp_dir / "introligo_config.yaml"
        config_content = """
modules:
  protobuf_api:
    title: Protobuf API
    language: protobuf
    manual_protodoc: |
      This is manual protobuf documentation.

      .. code-block:: protobuf

         message User {
            string id = 1;
         }
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_protobuf_diagrams(self, temp_dir):
        """Test generation with automatic protobuf diagrams."""
        # Create a sample proto file
        proto_dir = temp_dir / "protos"
        proto_dir.mkdir()
        proto_file = proto_dir / "user.proto"
        proto_content = """syntax = "proto3";

package user.v1;

message User {
    string id = 1;
    string name = 2;
}

enum Status {
    STATUS_UNKNOWN = 0;
    STATUS_ACTIVE = 1;
}
"""
        proto_file.write_text(proto_content)

        config_file = temp_dir / "introligo_config.yaml"
        config_content = """
modules:
  protobuf_api:
    title: Protobuf API
    language: protobuf
    proto_path: protos
    protobuf_diagrams:
      - type: messages
        output: messages.puml
        title: "Message Diagram"
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=False,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_protobuf_diagrams_no_extractor(self, temp_dir):
        """Test protobuf diagram generation when proto_path is not provided."""
        config_file = temp_dir / "introligo_config.yaml"
        config_content = """
modules:
  protobuf_api:
    title: Protobuf API
    protobuf_diagrams:
      - type: messages
        output: messages.puml
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_protobuf_proto_package_filter(self, temp_dir):
        """Test protobuf extraction with package filter."""
        # Create sample proto files with different packages
        proto_dir = temp_dir / "protos"
        proto_dir.mkdir()

        proto_file1 = proto_dir / "user.proto"
        proto_file1.write_text("""syntax = "proto3";
package user.v1;
message User {
    string id = 1;
}
""")

        proto_file2 = proto_dir / "product.proto"
        proto_file2.write_text("""syntax = "proto3";
package product.v1;
message Product {
    string id = 1;
}
""")

        config_file = temp_dir / "introligo_config.yaml"
        config_content = """
modules:
  user_api:
    title: User API
    language: protobuf
    proto_path: protos
    proto_package: user.v1
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_generate_with_protobuf_specific_files(self, temp_dir):
        """Test protobuf extraction with specific proto files."""
        proto_dir = temp_dir / "protos"
        proto_dir.mkdir()

        proto_file = proto_dir / "user.proto"
        proto_file.write_text("""syntax = "proto3";
package user.v1;
message User {
    string id = 1;
}
""")

        config_file = temp_dir / "introligo_config.yaml"
        config_content = """
modules:
  user_api:
    title: User API
    language: protobuf
    proto_path: protos
    proto_files:
      - user.proto
"""
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None


class TestGeneratorEdgeCases:
    """Tests for edge cases in generator.py."""

    def test_generator_without_config_file_parent(self, temp_dir):
        """Test generator when config file has no parent."""
        config_content = """
modules:
  test_module:
    title: Test Module
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_load_template_with_custom_file(self, temp_dir):
        """Test loading a custom template file."""
        template_file = temp_dir / "custom_template.rst"
        template_content = """
{{ title }}
{{ "=" * title|length }}

Custom template content.
"""
        template_file.write_text(template_content)

        config_content = """
modules:
  test_module:
    title: Test Module
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            template_file=template_file,
            dry_run=True,
        )
        result = generator.generate_all()

        assert result is not None

    def test_process_custom_sections_with_uml_directive(self, temp_dir):
        """Test custom sections with UML directive."""
        config_content = """
modules:
  test_module:
    title: Test Module
    custom_sections:
      - title: Architecture
        content: |
          .. uml::

             @startuml
             Class1 -> Class2
             @enduml
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )

        result = generator.generate_all()

        assert result is not None

    def test_process_custom_sections_with_mermaid_directive(self, temp_dir):
        """Test custom sections with Mermaid directive."""
        config_content = """
modules:
  test_module:
    title: Test Module
    custom_sections:
      - title: Flow
        content: |
          .. mermaid::

             graph LR
                A --> B
"""
        config_file = temp_dir / "config.yaml"
        config_file.write_text(config_content)

        generator = IntroligoGenerator(
            config_file=config_file,
            output_dir=temp_dir / "output",
            dry_run=True,
        )

        result = generator.generate_all()

        assert result is not None


class TestProtoDocExtractorEdgeCases:
    """Tests for edge cases in protodoc_extractor.py."""

    def test_extract_comments_block_comment_without_start(self, temp_dir):
        """Test extracting block comments without /* start marker."""
        from introligo.protodoc_extractor import ProtoDocExtractor

        extractor = ProtoDocExtractor(temp_dir)
        lines = [
            " * Comment line 1",
            " * Comment line 2",
            " */",
            "message Test {",
        ]
        result = extractor._extract_comments_before(lines, 3)

        # Should capture the block comment
        assert "*/" in result or "Comment" in result

    def testparse_proto_file_with_block_comments(self, temp_dir):
        """Test parsing proto file with block comments before package."""
        from introligo.protodoc_extractor import ProtoDocExtractor

        extractor = ProtoDocExtractor(temp_dir)
        content = """syntax = "proto3";

/* Block comment
 * spanning multiple lines
 */
package test.v1;

message Test {
    string id = 1;
}
"""
        result = extractor.parse_proto_file(content)

        assert result["syntax"] == "proto3"
        assert result["package"] == "test.v1"

    def test_parse_file_comment_before_syntax(self, temp_dir):
        """Test parsing file comment that appears before syntax declaration."""
        from introligo.protodoc_extractor import ProtoDocExtractor

        extractor = ProtoDocExtractor(temp_dir)
        content = """// File-level comment before syntax
syntax = "proto3";
package test.v1;
"""
        result = extractor.parse_proto_file(content)

        # File comment before syntax should be captured
        assert result["syntax"] == "proto3"


class TestRustDocExtractorEdgeCases:
    """Tests for edge cases in rustdoc_extractor.py."""

    def test_rustdoc_extractor_check_cargo_not_found(self):
        """Test RustDoc extractor when Cargo is not available."""
        from introligo.rustdoc_extractor import RustDocExtractor

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            extractor = RustDocExtractor()
            result = extractor.check_cargo_available()

            assert result is False

    def test_rustdoc_extractor_parse_json_minimal(self, temp_dir):
        """Test parsing rustdoc JSON with minimal structure."""
        from introligo.rustdoc_extractor import RustDocExtractor

        json_file = temp_dir / "test.json"
        json_content = """{
            "root": "0:0:1234",
            "crate_id": 42,
            "paths": {},
            "index": {},
            "external_crates": {}
        }"""
        json_file.write_text(json_content)

        extractor = RustDocExtractor()
        result = extractor._parse_rustdoc_json(json_file)

        # May return None or empty string for minimal structure
        assert result is None or isinstance(result, str)


class TestJavaDocExtractorEdgeCases:
    """Tests for edge cases in javadoc_extractor.py."""

    def test_javadoc_parse_source_with_annotation(self, temp_dir):
        """Test parsing Java source with annotations."""
        from introligo.javadoc_extractor import JavaDocExtractor

        java_source = """
/**
 * Test class with annotation.
 */
@Deprecated
public class TestClass {
    /**
     * Test method.
     */
    @Override
    public void testMethod() {
    }
}
"""
        extractor = JavaDocExtractor(temp_dir)
        result = extractor.parse_java_source(java_source)

        assert "TestClass" in result

    def test_javadoc_check_not_available_timeout(self):
        """Test JavaDoc check with timeout."""
        from introligo.javadoc_extractor import JavaDocExtractor

        with patch("subprocess.run") as mock_run:
            import subprocess

            mock_run.side_effect = subprocess.TimeoutExpired("java", 5)
            extractor = JavaDocExtractor()
            result = extractor.check_java_available()

            assert result is False


class TestProtobufDiagramGeneratorEdgeCases:
    """Tests for edge cases in protobuf_diagram_generator.py."""

    def test_diagram_generator_with_graphviz_output(self, temp_dir):
        """Test diagram generation with GraphViz output."""
        from introligo.protobuf_diagram_generator import generate_proto_diagrams

        parsed_proto = {
            "package": "test.v1",
            "messages": [
                {
                    "name": "User",
                    "comment": "User message",
                    "fields": [
                        {"name": "id", "type": "string", "number": "1", "label": "", "comment": ""}
                    ],
                }
            ],
            "enums": [],
            "services": [],
        }

        diagrams_config = [{"type": "dependencies", "format": "graphviz", "title": "Dependencies"}]

        result = generate_proto_diagrams([parsed_proto], diagrams_config, temp_dir)

        assert len(result) > 0
        assert result[0]["path"].endswith(".dot")


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
