"""Unit tests for protobuf_diagram_generator.py module."""

from pathlib import Path

import pytest

from introligo.protobuf_diagram_generator import (
    ProtobufDiagramGenerator,
    generate_proto_diagrams,
)


@pytest.fixture
def sample_parsed_files():
    """Provide sample parsed protobuf structures for testing."""
    return [
        {
            "package": "user.v1",
            "messages": [
                {
                    "name": "User",
                    "comment": "User entity",
                    "fields": [
                        {
                            "name": "id",
                            "type": "string",
                            "label": "",
                            "number": "1",
                            "comment": "User ID",
                            "keywords": {},
                        },
                        {
                            "name": "roles",
                            "type": "UserRole",
                            "label": "repeated",
                            "number": "2",
                            "comment": "User roles",
                            "keywords": {},
                        },
                        {
                            "name": "profile",
                            "type": "Profile",
                            "label": "",
                            "number": "3",
                            "comment": "User profile",
                            "keywords": {},
                        },
                    ],
                },
                {
                    "name": "Profile",
                    "comment": "User profile",
                    "fields": [
                        {
                            "name": "bio",
                            "type": "string",
                            "label": "",
                            "number": "1",
                            "comment": "Biography",
                            "keywords": {},
                        }
                    ],
                },
            ],
            "enums": [
                {
                    "name": "UserRole",
                    "comment": "User roles",
                    "values": [
                        {"name": "USER_ROLE_UNSPECIFIED", "number": "0", "comment": "Unspecified"},
                        {"name": "USER_ROLE_USER", "number": "1", "comment": "Regular user"},
                        {"name": "USER_ROLE_ADMIN", "number": "2", "comment": "Admin"},
                    ],
                }
            ],
            "services": [
                {
                    "name": "UserService",
                    "comment": "User management service",
                    "methods": [
                        {
                            "name": "GetUser",
                            "request_type": "GetUserRequest",
                            "response_type": "GetUserResponse",
                            "comment": "Get a user by ID",
                        },
                        {
                            "name": "CreateUser",
                            "request_type": "CreateUserRequest",
                            "response_type": "CreateUserResponse",
                            "comment": "Create a new user",
                        },
                        {
                            "name": "ListUsers",
                            "request_type": "ListUsersRequest",
                            "response_type": "ListUsersResponse",
                            "comment": "List all users",
                        },
                        {
                            "name": "UpdateUser",
                            "request_type": "UpdateUserRequest",
                            "response_type": "UpdateUserResponse",
                            "comment": "Update a user",
                        },
                        {
                            "name": "DeleteUser",
                            "request_type": "DeleteUserRequest",
                            "response_type": "DeleteUserResponse",
                            "comment": "Delete a user",
                        },
                    ],
                }
            ],
        },
        {
            "package": "product.v1",
            "messages": [
                {
                    "name": "Product",
                    "comment": "Product entity",
                    "fields": [
                        {
                            "name": "id",
                            "type": "string",
                            "label": "",
                            "number": "1",
                            "comment": "Product ID",
                            "keywords": {},
                        },
                        {
                            "name": "owner_id",
                            "type": "user.v1.User",
                            "label": "",
                            "number": "2",
                            "comment": "Product owner",
                            "keywords": {},
                        },
                    ],
                }
            ],
            "enums": [],
            "services": [
                {
                    "name": "ProductService",
                    "comment": "Product management service",
                    "methods": [
                        {
                            "name": "GetProduct",
                            "request_type": "GetProductRequest",
                            "response_type": "GetProductResponse",
                            "comment": "Get a product",
                        }
                    ],
                }
            ],
        },
    ]


class TestProtobufDiagramGenerator:
    """Test suite for ProtobufDiagramGenerator class."""

    def test_init(self):
        """Test generator initialization."""
        generator = ProtobufDiagramGenerator()
        assert generator.parsed_files == []

    def test_add_parsed_file(self):
        """Test adding a parsed file."""
        generator = ProtobufDiagramGenerator()
        parsed = {"package": "test.v1", "messages": []}
        generator.add_parsed_file(parsed)
        assert len(generator.parsed_files) == 1
        assert generator.parsed_files[0] == parsed

    def test_add_multiple_parsed_files(self):
        """Test adding multiple parsed files."""
        generator = ProtobufDiagramGenerator()
        parsed1 = {"package": "test1.v1", "messages": []}
        parsed2 = {"package": "test2.v1", "messages": []}
        generator.add_parsed_file(parsed1)
        generator.add_parsed_file(parsed2)
        assert len(generator.parsed_files) == 2

    def test_generate_class_diagram_basic(self, sample_parsed_files):
        """Test generating basic class diagram."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_class_diagram()

        assert "@startuml" in diagram
        assert "@enduml" in diagram
        assert "class User" in diagram
        assert "class Profile" in diagram
        assert "enum UserRole" in diagram

    def test_generate_class_diagram_with_title(self, sample_parsed_files):
        """Test generating class diagram with title."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_class_diagram(title="User Service Diagram")

        assert "title User Service Diagram" in diagram

    def test_generate_class_diagram_with_package_filter(self, sample_parsed_files):
        """Test generating class diagram with package filter."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_class_diagram(package_filter="user.v1")

        assert "User" in diagram
        assert "Product" not in diagram

    def test_generate_class_diagram_with_packages(self, sample_parsed_files):
        """Test that class diagram includes package grouping."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_class_diagram()

        assert 'package "user.v1"' in diagram
        assert 'package "product.v1"' in diagram

    def test_generate_class_diagram_with_relationships(self, sample_parsed_files):
        """Test that class diagram includes relationships."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_class_diagram()

        assert "' Relationships" in diagram
        # Check for composition relationships
        assert "*--" in diagram

    def test_generate_service_diagram_basic(self, sample_parsed_files):
        """Test generating basic service diagram."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_service_diagram()

        assert "@startuml" in diagram
        assert "@enduml" in diagram
        assert "interface UserService" in diagram
        assert "interface ProductService" in diagram

    def test_generate_service_diagram_with_title(self, sample_parsed_files):
        """Test generating service diagram with title."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_service_diagram(title="Services Overview")

        assert "title Services Overview" in diagram

    def test_generate_service_diagram_with_package_filter(self, sample_parsed_files):
        """Test generating service diagram with package filter."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_service_diagram(package_filter="user.v1")

        assert "UserService" in diagram
        assert "ProductService" not in diagram

    def test_generate_service_diagram_methods(self, sample_parsed_files):
        """Test that service diagram includes methods."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_service_diagram()

        assert "+GetUser" in diagram
        assert "+CreateUser" in diagram
        assert "GetUserRequest" in diagram
        assert "GetUserResponse" in diagram

    def test_generate_sequence_diagram_service_found(self, sample_parsed_files):
        """Test generating sequence diagram for existing service."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService")

        assert "@startuml" in diagram
        assert "@enduml" in diagram
        assert "title UserService RPC Flow" in diagram
        assert "actor Client" in diagram
        assert 'participant "UserService"' in diagram
        assert "database Storage" in diagram

    def test_generate_sequence_diagram_with_title(self, sample_parsed_files):
        """Test generating sequence diagram with custom title."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", title="Custom Title")

        assert "title Custom Title" in diagram

    def test_generate_sequence_diagram_specific_rpc(self, sample_parsed_files):
        """Test generating sequence diagram for specific RPC."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="GetUser")

        assert "== GetUser ==" in diagram
        assert "GetUserRequest" in diagram
        assert "Query data" in diagram
        # Should not include other methods
        assert "== CreateUser ==" not in diagram

    def test_generate_sequence_diagram_service_not_found(self):
        """Test generating sequence diagram for non-existent service."""
        generator = ProtobufDiagramGenerator()
        generator.add_parsed_file({"package": "test.v1", "services": []})

        diagram = generator.generate_sequence_diagram("NonExistentService")

        assert "Service 'NonExistentService' not found" in diagram

    def test_generate_sequence_diagram_create_method(self, sample_parsed_files):
        """Test sequence diagram for Create method."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="CreateUser")

        assert "Store data" in diagram

    def test_generate_sequence_diagram_get_method(self, sample_parsed_files):
        """Test sequence diagram for Get method."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="GetUser")

        assert "Query data" in diagram

    def test_generate_sequence_diagram_list_method(self, sample_parsed_files):
        """Test sequence diagram for List method."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="ListUsers")

        assert "Query data" in diagram

    def test_generate_sequence_diagram_update_method(self, sample_parsed_files):
        """Test sequence diagram for Update method."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="UpdateUser")

        assert "Update data" in diagram

    def test_generate_sequence_diagram_delete_method(self, sample_parsed_files):
        """Test sequence diagram for Delete method."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_sequence_diagram("UserService", rpc_name="DeleteUser")

        assert "Delete data" in diagram

    def test_generate_dependency_graph_graphviz(self, sample_parsed_files):
        """Test generating Graphviz dependency graph."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_dependency_graph(format="graphviz")

        assert "digraph ProtobufDependencies" in diagram
        assert "rankdir=LR" in diagram
        assert "user_v1" in diagram
        assert "product_v1" in diagram
        assert "->" in diagram  # Has dependencies

    def test_generate_dependency_graph_graphviz_with_title(self, sample_parsed_files):
        """Test generating Graphviz dependency graph with title."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_dependency_graph(
            title="Package Dependencies", format="graphviz"
        )

        assert 'label="Package Dependencies"' in diagram

    def test_generate_dependency_graph_plantuml(self, sample_parsed_files):
        """Test generating PlantUML dependency graph."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_dependency_graph(format="plantuml")

        assert "@startuml" in diagram
        assert "@enduml" in diagram
        assert 'package "user.v1"' in diagram
        assert 'package "product.v1"' in diagram
        assert "-->" in diagram

    def test_generate_dependency_graph_plantuml_with_title(self, sample_parsed_files):
        """Test generating PlantUML dependency graph with title."""
        generator = ProtobufDiagramGenerator()
        for parsed in sample_parsed_files:
            generator.add_parsed_file(parsed)

        diagram = generator.generate_dependency_graph(title="Dependencies", format="plantuml")

        assert "title Dependencies" in diagram

    def test_format_message_for_class_diagram(self):
        """Test formatting message for class diagram."""
        generator = ProtobufDiagramGenerator()
        message = {
            "name": "User",
            "fields": [
                {"name": "id", "type": "string", "label": ""},
                {"name": "tags", "type": "string", "label": "repeated"},
            ],
        }

        lines = generator._format_message_for_class_diagram(message)

        assert any("class User" in line for line in lines)
        assert any("+string id" in line for line in lines)
        assert any("+string[] tags" in line for line in lines)

    def test_format_message_with_optional_label(self):
        """Test formatting message with optional label."""
        generator = ProtobufDiagramGenerator()
        message = {
            "name": "User",
            "fields": [{"name": "id", "type": "string", "label": "optional"}],
        }

        lines = generator._format_message_for_class_diagram(message)

        assert any("+string id" in line for line in lines)

    def test_format_enum_for_class_diagram(self):
        """Test formatting enum for class diagram."""
        generator = ProtobufDiagramGenerator()
        enum = {"name": "Status", "values": [{"name": "STATUS_UNKNOWN"}, {"name": "STATUS_ACTIVE"}]}

        lines = generator._format_enum_for_class_diagram(enum)

        assert any("enum Status" in line for line in lines)
        assert any("STATUS_UNKNOWN" in line for line in lines)
        assert any("STATUS_ACTIVE" in line for line in lines)

    def test_format_service_component(self):
        """Test formatting service component."""
        generator = ProtobufDiagramGenerator()
        service = {
            "name": "UserService",
            "methods": [
                {
                    "name": "GetUser",
                    "request_type": "GetUserRequest",
                    "response_type": "GetUserResponse",
                }
            ],
        }

        lines = generator._format_service_component(service, "user.v1")

        assert any('package "user.v1"' in line for line in lines)
        assert any("interface UserService" in line for line in lines)
        assert any("+GetUser(GetUserRequest): GetUserResponse" in line for line in lines)

    def test_format_service_component_no_package(self):
        """Test formatting service component without package."""
        generator = ProtobufDiagramGenerator()
        service = {"name": "UserService", "methods": []}

        lines = generator._format_service_component(service, "")

        assert not any("package" in line for line in lines)
        assert any("interface UserService" in line for line in lines)

    def test_extract_relationships_with_message_type(self):
        """Test extracting relationships with message types."""
        generator = ProtobufDiagramGenerator()
        message = {
            "name": "User",
            "fields": [
                {"name": "profile", "type": "Profile", "label": ""},
                {"name": "roles", "type": "Role", "label": "repeated"},
            ],
        }

        lines = generator._extract_relationships(message, "user.v1")

        assert len(lines) == 2
        assert 'User "1" *-- "1" Profile' in lines
        assert 'User "1" *-- "*" Role' in lines

    def test_extract_relationships_with_primitive_type(self):
        """Test that primitives don't create relationships."""
        generator = ProtobufDiagramGenerator()
        message = {
            "name": "User",
            "fields": [
                {"name": "id", "type": "string", "label": ""},
                {"name": "age", "type": "int32", "label": ""},
            ],
        }

        lines = generator._extract_relationships(message, "user.v1")

        assert len(lines) == 0

    def test_is_message_type_primitives(self):
        """Test identifying primitive types."""
        generator = ProtobufDiagramGenerator()

        assert generator._is_message_type("string") is False
        assert generator._is_message_type("int32") is False
        assert generator._is_message_type("int64") is False
        assert generator._is_message_type("bool") is False
        assert generator._is_message_type("float") is False
        assert generator._is_message_type("double") is False
        assert generator._is_message_type("bytes") is False

    def test_is_message_type_all_primitives(self):
        """Test all primitive types."""
        generator = ProtobufDiagramGenerator()
        primitives = [
            "int32",
            "int64",
            "uint32",
            "uint64",
            "sint32",
            "sint64",
            "fixed32",
            "fixed64",
            "sfixed32",
            "sfixed64",
            "float",
            "double",
            "bool",
            "string",
            "bytes",
        ]

        for prim in primitives:
            assert generator._is_message_type(prim) is False

    def test_is_message_type_custom(self):
        """Test identifying custom message types."""
        generator = ProtobufDiagramGenerator()

        assert generator._is_message_type("User") is True
        assert generator._is_message_type("Product") is True
        assert generator._is_message_type("user.v1.User") is True

    def test_is_message_type_map(self):
        """Test that map types are not message types."""
        generator = ProtobufDiagramGenerator()

        assert generator._is_message_type("map<string, string>") is False
        assert generator._is_message_type("map<int32, User>") is False

    def test_extract_package_from_type_qualified(self):
        """Test extracting package from qualified type."""
        generator = ProtobufDiagramGenerator()

        result = generator._extract_package_from_type("user.v1.User")
        assert result == "user.v1"

    def test_extract_package_from_type_simple(self):
        """Test extracting package from simple type."""
        generator = ProtobufDiagramGenerator()

        result = generator._extract_package_from_type("User")
        assert result is None

    def test_extract_package_from_type_nested(self):
        """Test extracting package from nested qualified type."""
        generator = ProtobufDiagramGenerator()

        result = generator._extract_package_from_type("com.example.user.v1.User")
        assert result == "com.example.user.v1"


class TestGenerateProtoDiagrams:
    """Test suite for generate_proto_diagrams function."""

    def test_generate_proto_diagrams_class(self, temp_dir, sample_parsed_files):
        """Test generating class diagrams."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "class", "title": "User Classes"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1
        assert result[0]["type"] == "class"
        assert result[0]["title"] == "User Classes"
        assert "path" in result[0]

        # Check that file was created
        diagrams_dir = output_dir / "diagrams" / "generated"
        assert diagrams_dir.exists()
        assert len(list(diagrams_dir.glob("*.puml"))) == 1

    def test_generate_proto_diagrams_service(self, temp_dir, sample_parsed_files):
        """Test generating service diagrams."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "service", "package": "user.v1"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1
        assert result[0]["type"] == "service"

    def test_generate_proto_diagrams_sequence(self, temp_dir, sample_parsed_files):
        """Test generating sequence diagrams."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [
            {"type": "sequence", "service": "UserService", "title": "User Service Flow"}
        ]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1
        assert result[0]["type"] == "sequence"

    def test_generate_proto_diagrams_sequence_no_service(self, temp_dir, sample_parsed_files):
        """Test generating sequence diagram without service name."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [
            {"type": "sequence"}  # Missing 'service' parameter
        ]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        # Should skip this diagram
        assert len(result) == 0

    def test_generate_proto_diagrams_dependencies_graphviz(self, temp_dir, sample_parsed_files):
        """Test generating Graphviz dependency diagram."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "dependencies", "format": "graphviz", "title": "Dependencies"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1
        assert result[0]["type"] == "dependencies"

        # Check for .dot file
        diagrams_dir = output_dir / "diagrams" / "generated"
        assert len(list(diagrams_dir.glob("*.dot"))) == 1

    def test_generate_proto_diagrams_dependencies_plantuml(self, temp_dir, sample_parsed_files):
        """Test generating PlantUML dependency diagram."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "dependencies", "format": "plantuml"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1

        # Check for .puml file
        diagrams_dir = output_dir / "diagrams" / "generated"
        assert len(list(diagrams_dir.glob("*.puml"))) == 1

    def test_generate_proto_diagrams_unknown_type(self, temp_dir, sample_parsed_files):
        """Test handling unknown diagram type."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "unknown_type"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        # Should skip unknown type
        assert len(result) == 0

    def test_generate_proto_diagrams_multiple(self, temp_dir, sample_parsed_files):
        """Test generating multiple diagrams."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [
            {"type": "class", "title": "Classes"},
            {"type": "service", "title": "Services"},
            {"type": "dependencies", "format": "graphviz"},
        ]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 3

    def test_generate_proto_diagrams_with_package_filter(self, temp_dir, sample_parsed_files):
        """Test generating diagrams with package filter."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "class", "package": "user.v1", "title": "User Package"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1

        # Check file content
        diagrams_dir = output_dir / "diagrams" / "generated"
        puml_files = list(diagrams_dir.glob("*.puml"))
        assert len(puml_files) == 1

        content = puml_files[0].read_text()
        assert "User" in content
        assert "Product" not in content

    def test_generate_proto_diagrams_filename_generation(self, temp_dir, sample_parsed_files):
        """Test filename generation from title."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [
            {"type": "class", "title": "User Service Classes"},
            {"type": "service"},  # No title
        ]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 2

        # Check filenames
        diagrams_dir = output_dir / "diagrams" / "generated"
        files = list(diagrams_dir.glob("*.puml"))
        filenames = [f.name for f in files]

        assert any("user_service_classes" in name for name in filenames)
        assert any("service_diagram" in name for name in filenames)

    def test_generate_proto_diagrams_filename_with_package(self, temp_dir, sample_parsed_files):
        """Test filename generation with package filter."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "class", "package": "user.v1", "title": "Classes"}]

        generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        # Check filename includes package
        diagrams_dir = output_dir / "diagrams" / "generated"
        files = list(diagrams_dir.glob("*.puml"))
        assert len(files) == 1
        assert "user_v1" in files[0].name

    def test_generate_proto_diagrams_creates_directories(self, temp_dir, sample_parsed_files):
        """Test that function creates necessary directories."""
        output_dir = temp_dir / "output"
        # Don't create output_dir - function should create it

        diagram_configs = [{"type": "class"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1

        # Check directories were created
        diagrams_dir = output_dir / "diagrams" / "generated"
        assert diagrams_dir.exists()
        assert diagrams_dir.is_dir()

    def test_generate_proto_diagrams_relative_path(self, temp_dir, sample_parsed_files):
        """Test that returned paths are relative."""
        output_dir = temp_dir / "output"
        output_dir.mkdir()

        diagram_configs = [{"type": "class"}]

        result = generate_proto_diagrams(sample_parsed_files, diagram_configs, output_dir)

        assert len(result) == 1
        path = result[0]["path"]

        # Path should be relative
        assert not Path(path).is_absolute()
        assert "diagrams/generated" in path
