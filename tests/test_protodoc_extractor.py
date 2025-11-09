"""Unit tests for protodoc_extractor.py module."""

import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from introligo.protodoc_extractor import ProtoDocExtractor


@pytest.fixture
def temp_proto_dir(temp_dir):
    """Create a temporary directory with sample proto files."""
    proto_dir = temp_dir / "protos"
    proto_dir.mkdir()

    # Sample proto file with comprehensive examples
    sample_proto = proto_dir / "user.proto"
    proto_content = """syntax = "proto3";

// User management service for handling user accounts.
// This is a multi-line comment.
package user.v1;

// User message representing a user account.
// @Ref UserRole for role information.
message User {
    // Unique identifier.
    // @Pattern ^[a-z0-9-]+$
    // @MinLength 1
    // @MaxLength 36
    string id = 1;

    // User's email address.
    // @Example user@example.com
    string email = 2;  // Inline comment for email

    // User's display name.
    string name = 3;

    // User's role in the system.
    UserRole role = 4;

    /*
     * Account creation timestamp.
     * @Minimum 0
     */
    int64 created_at = 5;

    // Repeated field example.
    // @MinItems 0
    // @MaxItems 10
    repeated string tags = 6;
}

// User roles enum.
enum UserRole {
    // Default unspecified role.
    USER_ROLE_UNSPECIFIED = 0;
    // Regular user role.
    USER_ROLE_USER = 1;
    // Administrator role.
    USER_ROLE_ADMIN = 2;
}

// User service for CRUD operations.
service UserService {
    // Creates a new user.
    rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);

    /* Gets a user by ID.
     * Returns the user if found.
     */
    rpc GetUser(GetUserRequest) returns (GetUserResponse);

    // Updates an existing user.
    rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);  // Inline comment
}

// Request message for creating a user.
message CreateUserRequest {
    string email = 1;
    string name = 2;
}

// Response message for creating a user.
message CreateUserResponse {
    User user = 1;
}

// Request message for getting a user.
message GetUserRequest {
    string id = 1;
}

// Response message for getting a user.
message GetUserResponse {
    User user = 1;
}

// Request message for updating a user.
message UpdateUserRequest {
    string id = 1;
    string email = 2;
}

// Response message for updating a user.
message UpdateUserResponse {
    User user = 1;
}
"""
    sample_proto.write_text(proto_content)

    # Another proto file in different package
    other_proto = proto_dir / "product.proto"
    other_content = """syntax = "proto3";

package product.v1;

message Product {
    string id = 1;
    string name = 2;
}
"""
    other_proto.write_text(other_content)

    return proto_dir


class TestProtoDocExtractor:
    """Test suite for ProtoDocExtractor class."""

    def test_init_with_path(self, temp_proto_dir):
        """Test extractor initialization with a proto path."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        assert extractor.proto_path == temp_proto_dir

    def test_init_without_path(self):
        """Test extractor initialization without a proto path."""
        extractor = ProtoDocExtractor()
        assert extractor.proto_path is None

    def test_check_protoc_available_true(self):
        """Test checking protoc availability when it's installed."""
        extractor = ProtoDocExtractor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert extractor.check_protoc_available() is True
            mock_run.assert_called_once()

    def test_check_protoc_available_false(self):
        """Test checking protoc availability when it's not installed."""
        extractor = ProtoDocExtractor()

        with patch("subprocess.run", side_effect=FileNotFoundError()):
            assert extractor.check_protoc_available() is False

    def test_check_protoc_available_timeout(self):
        """Test checking protoc availability with timeout."""
        extractor = ProtoDocExtractor()

        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("cmd", 5)):
            assert extractor.check_protoc_available() is False

    def test_check_protoc_gen_doc_available_true(self):
        """Test checking protoc-gen-doc availability when installed."""
        extractor = ProtoDocExtractor()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            assert extractor.check_protoc_gen_doc_available() is True

    def test_check_protoc_gen_doc_available_false(self):
        """Test checking protoc-gen-doc availability when not installed."""
        extractor = ProtoDocExtractor()

        with patch("subprocess.run", side_effect=FileNotFoundError()):
            assert extractor.check_protoc_gen_doc_available() is False

    def test_find_proto_files_no_path(self):
        """Test finding proto files when no path is set."""
        extractor = ProtoDocExtractor()
        result = extractor.find_proto_files()
        assert result == []

    def test_find_proto_files_nonexistent_path(self):
        """Test finding proto files when path doesn't exist."""
        extractor = ProtoDocExtractor(Path("/nonexistent/path"))
        result = extractor.find_proto_files()
        assert result == []

    def test_find_proto_files_all(self, temp_proto_dir):
        """Test finding all proto files recursively."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        result = extractor.find_proto_files()
        assert len(result) == 2
        assert any(p.name == "user.proto" for p in result)
        assert any(p.name == "product.proto" for p in result)

    def test_find_proto_files_specific(self, temp_proto_dir):
        """Test finding specific proto files."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        result = extractor.find_proto_files(["user.proto"])
        assert len(result) == 1
        assert result[0].name == "user.proto"

    def test_find_proto_files_absolute_path(self, temp_proto_dir):
        """Test finding proto files with absolute paths."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        user_proto = temp_proto_dir / "user.proto"
        result = extractor.find_proto_files([str(user_proto)])
        assert len(result) == 1
        assert result[0].name == "user.proto"

    def test_normalize_comment_inline(self):
        """Test normalizing inline comments."""
        extractor = ProtoDocExtractor()
        comment = "// This is a comment"
        result = extractor._normalize_comment(comment)
        assert result == "This is a comment"

    def test_normalize_comment_block(self):
        """Test normalizing block comments."""
        extractor = ProtoDocExtractor()
        comment = "/* This is a\n * multi-line\n * comment */"
        result = extractor._normalize_comment(comment)
        assert "multi-line" in result
        assert "comment" in result

    def test_normalize_comment_mixed(self):
        """Test normalizing mixed comment styles."""
        extractor = ProtoDocExtractor()
        comment = "// Line 1\n// Line 2\n// Line 3"
        result = extractor._normalize_comment(comment)
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_process_cross_references(self):
        """Test processing @Ref keywords."""
        extractor = ProtoDocExtractor()
        text = "See @Ref User for details and @Ref UserRole for roles."
        result = extractor._process_cross_references(text)
        assert ":ref:`User <proto-User>`" in result
        assert ":ref:`UserRole <proto-UserRole>`" in result

    def test_process_cross_references_dotted(self):
        """Test processing @Ref with dotted names."""
        extractor = ProtoDocExtractor()
        text = "See @Ref user.v1.User for details."
        result = extractor._process_cross_references(text)
        assert ":ref:`user.v1.User <proto-user.v1.User>`" in result

    def test_parse_asyncapi_keywords_single(self):
        """Test parsing single AsyncAPI keyword."""
        extractor = ProtoDocExtractor()
        comment = "User ID field.\n@Pattern ^[a-z0-9-]+$"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert desc == "User ID field."
        assert keywords["pattern"] == "^[a-z0-9-]+$"

    def test_parse_asyncapi_keywords_multiple(self):
        """Test parsing multiple AsyncAPI keywords."""
        extractor = ProtoDocExtractor()
        comment = "Field description.\n@Min 0\n@Max 100\n@Example 42\n@Default 10"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert desc == "Field description."
        assert keywords["minimum"] == "0"
        assert keywords["maximum"] == "100"
        assert keywords["example"] == "42"
        assert keywords["default"] == "10"

    def test_parse_asyncapi_keywords_aliases(self):
        """Test parsing AsyncAPI keyword aliases."""
        extractor = ProtoDocExtractor()
        comment = "Field.\n@Minimum 1\n@Maximum 10"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert keywords["minimum"] == "1"
        assert keywords["maximum"] == "10"

    def test_parse_asyncapi_keywords_collection(self):
        """Test parsing collection-related keywords."""
        extractor = ProtoDocExtractor()
        comment = "Tags field.\n@MinItems 0\n@MaxItems 10\n@MinLength 1\n@MaxLength 50"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert keywords["minItems"] == "0"
        assert keywords["maxItems"] == "10"
        assert keywords["minLength"] == "1"
        assert keywords["maxLength"] == "50"

    def test_parse_asyncapi_keywords_exclusive(self):
        """Test parsing exclusive min/max keywords."""
        extractor = ProtoDocExtractor()
        comment = "Value.\n@ExclusiveMinimum 0\n@ExclusiveMaximum 100"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert keywords["exclusiveMinimum"] == "0"
        assert keywords["exclusiveMaximum"] == "100"

    def test_parse_asyncapi_keywords_with_colon(self):
        """Test parsing keywords with colon separator."""
        extractor = ProtoDocExtractor()
        comment = "Field.\n@Pattern: ^test$\n@Example: test"
        desc, keywords = extractor._parse_asyncapi_keywords(comment)
        assert keywords["pattern"] == "^test$"
        assert keywords["example"] == "test"

    def test_extract_comments_before_inline(self, temp_proto_dir):
        """Test extracting inline comments before a line."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        lines = [
            "",
            "// Comment 1",
            "// Comment 2",
            "message Test {",
        ]
        result = extractor._extract_comments_before(lines, 3)
        assert "// Comment 1" in result
        assert "// Comment 2" in result

    def test_extract_comments_before_block(self, temp_proto_dir):
        """Test extracting block comments before a line."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        lines = [
            "/* Block comment",
            " * Line 2",
            " */",
            "message Test {",
        ]
        result = extractor._extract_comments_before(lines, 3)
        assert "Block comment" in result

    def test_extract_comments_before_with_empty_lines(self, temp_proto_dir):
        """Test extracting comments with empty lines in between."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        lines = [
            "// Comment 1",
            "// Comment 2",
            "",
            "message Test {",
        ]
        result = extractor._extract_comments_before(lines, 3)
        assert "// Comment 1" in result
        assert "// Comment 2" in result

    def test_extract_inline_comment(self):
        """Test extracting inline comment from a line."""
        extractor = ProtoDocExtractor()
        line = "string name = 1;  // This is the name field"
        line_without, comment = extractor._extract_inline_comment(line)
        assert "string name = 1;" in line_without
        assert comment == "This is the name field"

    def test_extract_inline_comment_no_comment(self):
        """Test extracting when there's no inline comment."""
        extractor = ProtoDocExtractor()
        line = "string name = 1;"
        line_without, comment = extractor._extract_inline_comment(line)
        assert line_without == line
        assert comment == ""

    def testparse_proto_file(self, temp_proto_dir):
        """Test parsing a complete proto file."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        proto_file = temp_proto_dir / "user.proto"
        with open(proto_file) as f:
            content = f.read()

        result = extractor.parse_proto_file(content)

        assert result["syntax"] == "proto3"
        assert result["package"] == "user.v1"
        assert "User management service" in result["file_comment"]
        assert len(result["messages"]) > 0
        assert len(result["enums"]) > 0
        assert len(result["services"]) > 0

    def test_parse_messages(self, temp_proto_dir):
        """Test parsing messages from proto content."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        content = """
        // User message
        message User {
            string id = 1;
            string name = 2;
        }
        """
        lines = content.split("\n")
        result = extractor._parse_messages(content, lines)

        assert len(result) == 1
        assert result[0]["name"] == "User"
        assert "User message" in result[0]["comment"]
        assert len(result[0]["fields"]) == 2

    def test_parse_fields(self):
        """Test parsing fields from a message body."""
        extractor = ProtoDocExtractor()
        body = """
            // Field 1 comment
            string field1 = 1;
            // Field 2 comment
            repeated int32 field2 = 2;
            optional bool field3 = 3;  // Inline comment
        """
        body_lines = body.split("\n")
        result = extractor._parse_fields(body, body_lines)

        assert len(result) == 3
        assert result[0]["name"] == "field1"
        assert result[0]["type"] == "string"
        assert result[1]["label"] == "repeated"
        assert result[2]["label"] == "optional"

    def test_parse_fields_with_keywords(self):
        """Test parsing fields with AsyncAPI keywords."""
        extractor = ProtoDocExtractor()
        body = """
            // ID field
            // @Pattern ^[0-9]+$
            // @MinLength 1
            string id = 1;
        """
        body_lines = body.split("\n")
        result = extractor._parse_fields(body, body_lines)

        assert len(result) == 1
        assert result[0]["comment"] == "ID field"
        assert "pattern" in result[0]["keywords"]
        assert "minLength" in result[0]["keywords"]

    def test_parse_enums(self):
        """Test parsing enums from proto content."""
        extractor = ProtoDocExtractor()
        content = """
        // Status enum
        enum Status {
            STATUS_UNKNOWN = 0;
            STATUS_ACTIVE = 1;
        }
        """
        lines = content.split("\n")
        result = extractor._parse_enums(content, lines)

        assert len(result) == 1
        assert result[0]["name"] == "Status"
        assert "Status enum" in result[0]["comment"]
        assert len(result[0]["values"]) == 2

    def test_parse_enum_values(self):
        """Test parsing enum values."""
        extractor = ProtoDocExtractor()
        body = """
            // Unknown value
            STATUS_UNKNOWN = 0;
            // Active value
            STATUS_ACTIVE = 1;
        """
        body_lines = body.split("\n")
        result = extractor._parse_enum_values(body, body_lines)

        assert len(result) == 2
        assert result[0]["name"] == "STATUS_UNKNOWN"
        assert result[0]["number"] == "0"
        assert "Unknown value" in result[0]["comment"]

    def test_parse_services(self):
        """Test parsing services from proto content."""
        extractor = ProtoDocExtractor()
        content = """
        // User service
        service UserService {
            rpc GetUser(GetUserRequest) returns (GetUserResponse);
        }
        """
        lines = content.split("\n")
        result = extractor._parse_services(content, lines)

        assert len(result) == 1
        assert result[0]["name"] == "UserService"
        assert "User service" in result[0]["comment"]
        assert len(result[0]["methods"]) == 1

    def test_parse_rpc_methods(self):
        """Test parsing RPC methods."""
        extractor = ProtoDocExtractor()
        body = """
            // Get user method
            rpc GetUser(GetUserRequest) returns (GetUserResponse);
            // Create user method
            rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
        """
        body_lines = body.split("\n")
        result = extractor._parse_rpc_methods(body, body_lines)

        assert len(result) == 2
        assert result[0]["name"] == "GetUser"
        assert result[0]["request_type"] == "GetUserRequest"
        assert result[0]["response_type"] == "GetUserResponse"
        assert "Get user method" in result[0]["comment"]

    def test_format_message(self):
        """Test formatting a message as RST."""
        extractor = ProtoDocExtractor()
        message = {
            "name": "User",
            "comment": "User message",
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                    "label": "",
                    "number": "1",
                    "comment": "User ID",
                    "keywords": {"pattern": "^[0-9]+$"},
                }
            ],
        }
        result = extractor._format_message(message)

        assert any("User" in line for line in result)
        assert any("message User" in line for line in result)
        assert any("id" in line for line in result)
        assert any("pattern" in line for line in result)

    def test_format_enum(self):
        """Test formatting an enum as RST."""
        extractor = ProtoDocExtractor()
        enum = {
            "name": "Status",
            "comment": "Status enum",
            "values": [
                {"name": "STATUS_UNKNOWN", "number": "0", "comment": "Unknown"},
                {"name": "STATUS_ACTIVE", "number": "1", "comment": "Active"},
            ],
        }
        result = extractor._format_enum(enum)

        assert any("Status" in line for line in result)
        assert any("enum Status" in line for line in result)
        assert any("STATUS_UNKNOWN" in line for line in result)

    def test_format_service_new(self):
        """Test formatting a service as RST."""
        extractor = ProtoDocExtractor()
        service = {
            "name": "UserService",
            "comment": "User service",
            "methods": [
                {
                    "name": "GetUser",
                    "request_type": "GetUserRequest",
                    "response_type": "GetUserResponse",
                    "comment": "Gets a user",
                }
            ],
        }
        result = extractor._format_service_new(service)

        assert any("UserService" in line for line in result)
        assert any("service UserService" in line for line in result)
        assert any("GetUser" in line for line in result)

    def test_format_parsed_proto(self):
        """Test formatting parsed proto structure."""
        extractor = ProtoDocExtractor()
        parsed = {
            "file_comment": "Test file",
            "package": "test.v1",
            "messages": [{"name": "Test", "comment": "Test message", "fields": []}],
            "enums": [],
            "services": [],
        }
        result = extractor._format_parsed_proto(parsed, "test.proto")

        assert len(result) > 0
        assert any("Test file" in line for line in result)
        assert any("test.v1" in line for line in result)

    def test_extract_proto_doc_no_path(self):
        """Test extracting proto doc with no path set."""
        extractor = ProtoDocExtractor()
        result = extractor.extract_proto_doc()
        assert result is None

    def test_extract_proto_doc_with_files(self, temp_proto_dir):
        """Test extracting proto doc from specific files."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        result = extractor.extract_proto_doc(proto_files=["user.proto"])
        assert result is not None
        assert "User" in result
        assert "UserService" in result

    def test_extract_proto_doc_with_package_filter(self, temp_proto_dir):
        """Test extracting proto doc with package filter."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        result = extractor.extract_proto_doc(package_name="user.v1")
        assert result is not None
        assert "user.v1" in result

    def test_parse_proto_sources_no_files(self):
        """Test parsing proto sources when no files found."""
        extractor = ProtoDocExtractor(Path("/nonexistent"))
        result = extractor._parse_proto_sources()
        assert result == ""

    def test_parse_proto_sources_with_error(self, temp_proto_dir):
        """Test parsing proto sources with an error."""
        extractor = ProtoDocExtractor(temp_proto_dir)

        with patch.object(extractor, "find_proto_files", side_effect=Exception("Test error")):
            result = extractor._parse_proto_sources()
            assert result == ""

    def test_convert_to_rst_empty(self):
        """Test converting empty proto doc to RST."""
        extractor = ProtoDocExtractor()
        result = extractor.convert_to_rst(None)
        assert result == ""

    def test_convert_to_rst_with_content(self):
        """Test converting proto doc to RST."""
        extractor = ProtoDocExtractor()
        content = "Test documentation"
        result = extractor.convert_to_rst(content)
        assert result == content

    def test_extract_and_convert_success(self, temp_proto_dir):
        """Test successful extraction and conversion."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        success, rst_content = extractor.extract_and_convert(["user.proto"])

        assert success is True
        assert "User" in rst_content
        assert "UserService" in rst_content

    def test_extract_and_convert_failure(self):
        """Test failed extraction and conversion."""
        extractor = ProtoDocExtractor(Path("/nonexistent"))
        success, rst_content = extractor.extract_and_convert()

        assert success is False
        assert "note::" in rst_content
        assert "protoc" in rst_content

    def test_extract_and_convert_with_package(self, temp_proto_dir):
        """Test extraction with specific package name."""
        extractor = ProtoDocExtractor(temp_proto_dir)
        success, rst_content = extractor.extract_and_convert(package_name="user.v1")

        assert success is True
        assert "user.v1" in rst_content

    def test_parse_protoc_gen_doc_json_valid(self, temp_dir):
        """Test parsing valid protoc-gen-doc JSON."""
        extractor = ProtoDocExtractor()

        json_file = temp_dir / "proto.json"
        json_content = """{
            "files": [{
                "name": "user.proto",
                "description": "User proto file",
                "package": "user.v1",
                "messages": [{
                    "name": "User",
                    "fullName": "user.v1.User",
                    "description": "User message",
                    "fields": [{
                        "name": "id",
                        "type": "string",
                        "label": "optional",
                        "number": "1",
                        "description": "User ID"
                    }]
                }],
                "enums": [{
                    "name": "Status",
                    "fullName": "user.v1.Status",
                    "description": "Status enum",
                    "values": [{
                        "name": "STATUS_UNKNOWN",
                        "number": "0",
                        "description": "Unknown status"
                    }]
                }],
                "services": [{
                    "name": "UserService",
                    "fullName": "user.v1.UserService",
                    "description": "User service",
                    "methods": [{
                        "name": "GetUser",
                        "description": "Get user method",
                        "requestType": "GetUserRequest",
                        "responseType": "GetUserResponse"
                    }]
                }]
            }]
        }"""
        json_file.write_text(json_content)

        result = extractor._parse_protoc_gen_doc_json(json_file)

        assert result is not None
        assert "User message" in result
        assert "Status enum" in result
        assert "UserService" in result

    def test_parse_protoc_gen_doc_json_with_package_filter(self, temp_dir):
        """Test parsing JSON with package filter."""
        extractor = ProtoDocExtractor()

        json_file = temp_dir / "proto.json"
        json_content = """{
            "files": [
                {
                    "name": "user.proto",
                    "package": "user.v1",
                    "messages": [{"name": "User"}]
                },
                {
                    "name": "product.proto",
                    "package": "product.v1",
                    "messages": [{"name": "Product"}]
                }
            ]
        }"""
        json_file.write_text(json_content)

        result = extractor._parse_protoc_gen_doc_json(json_file, package_name="user.v1")

        assert result is not None
        assert "User" in result
        # Product should be filtered out
        assert "Product" not in result

    def test_parse_protoc_gen_doc_json_invalid(self, temp_dir):
        """Test parsing invalid JSON."""
        extractor = ProtoDocExtractor()

        json_file = temp_dir / "invalid.json"
        json_file.write_text("invalid json")

        result = extractor._parse_protoc_gen_doc_json(json_file)
        assert result is None

    def test_parse_protoc_gen_doc_json_missing_file(self):
        """Test parsing non-existent JSON file."""
        extractor = ProtoDocExtractor()

        result = extractor._parse_protoc_gen_doc_json(Path("/nonexistent.json"))
        assert result is None

    def test_format_message_from_json(self):
        """Test formatting message from protoc-gen-doc JSON format."""
        extractor = ProtoDocExtractor()
        doc_parts: list[str] = []
        message = {
            "name": "User",
            "fullName": "user.v1.User",
            "description": "User message",
            "fields": [
                {
                    "name": "id",
                    "type": "string",
                    "label": "optional",
                    "number": "1",
                    "description": "User ID",
                }
            ],
        }

        extractor._format_message_json(message, doc_parts)

        result = "\n".join(doc_parts)
        assert "User" in result
        assert "message user.v1.User" in result
        assert "id" in result

    def test_format_message_nested(self):
        """Test formatting nested messages."""
        extractor = ProtoDocExtractor()
        doc_parts: list[str] = []
        message = {
            "name": "Outer",
            "fullName": "Outer",
            "fields": [],
            "messages": [{"name": "Inner", "fullName": "Outer.Inner", "fields": []}],
        }

        extractor._format_message_json(message, doc_parts, indent=0)

        result = "\n".join(doc_parts)
        assert "Outer" in result
        assert "Inner" in result

    def test_format_enum_from_json(self):
        """Test formatting enum from JSON format."""
        extractor = ProtoDocExtractor()
        doc_parts: list[str] = []
        enum = {
            "name": "Status",
            "fullName": "Status",
            "description": "Status enum",
            "values": [{"name": "STATUS_UNKNOWN", "number": "0", "description": "Unknown"}],
        }

        extractor._format_enum_json(enum, doc_parts)

        result = "\n".join(doc_parts)
        assert "Status" in result
        assert "enum Status" in result
        assert "STATUS_UNKNOWN" in result

    def test_format_service_from_json(self):
        """Test formatting service from JSON format."""
        extractor = ProtoDocExtractor()
        doc_parts: list[str] = []
        service = {
            "name": "UserService",
            "fullName": "UserService",
            "description": "User service",
            "methods": [
                {
                    "name": "GetUser",
                    "description": "Get user",
                    "requestType": "GetUserRequest",
                    "responseType": "GetUserResponse",
                }
            ],
        }

        extractor._format_service(service, doc_parts)

        result = "\n".join(doc_parts)
        assert "UserService" in result
        assert "GetUser" in result
        assert "GetUserRequest" in result
