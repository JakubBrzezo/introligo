"""Tests for PageNode class."""

from pathlib import Path

from introligo import PageNode


class TestPageNode:
    """Test cases for PageNode class."""

    def test_pagenode_basic_initialization(self):
        """Test basic PageNode initialization."""
        config = {"title": "Test Module", "module": "test.module"}
        node = PageNode("test_id", config)

        assert node.page_id == "test_id"
        assert node.config == config
        assert node.title == "Test Module"
        assert node.parent is None
        assert node.children == []

    def test_pagenode_title_from_id(self):
        """Test that title defaults to page_id if not provided."""
        config = {"module": "test.module"}
        node = PageNode("my_module", config)

        assert node.title == "my_module"

    def test_pagenode_slug_generation(self):
        """Test slug generation from title."""
        config = {"title": "My Test Module"}
        node = PageNode("test", config)

        assert node.slug == "my_test_module"

    def test_pagenode_with_parent(self):
        """Test PageNode with parent relationship."""
        parent_config = {"title": "Parent"}
        parent = PageNode("parent_id", parent_config)

        child_config = {"title": "Child"}
        child = PageNode("child_id", child_config, parent=parent)

        assert child.parent == parent

    def test_pagenode_children_management(self):
        """Test adding children to PageNode."""
        parent_config = {"title": "Parent"}
        parent = PageNode("parent_id", parent_config)

        child1_config = {"title": "Child 1"}
        child1 = PageNode("child1", child1_config)
        parent.children.append(child1)

        child2_config = {"title": "Child 2"}
        child2 = PageNode("child2", child2_config)
        parent.children.append(child2)

        assert len(parent.children) == 2
        assert child1 in parent.children
        assert child2 in parent.children

    def test_get_rst_filename(self):
        """Test RST filename generation."""
        config = {"title": "My Module"}
        node = PageNode("test", config)

        filename = node.get_rst_filename()
        assert filename == "my_module.rst"

    def test_get_output_dir_no_parent(self):
        """Test output directory for root node."""
        config = {"title": "Root Module"}
        node = PageNode("root", config)
        base_dir = Path("/tmp/generated")

        output_dir = node.get_output_dir(base_dir)
        assert output_dir == base_dir

    def test_get_output_dir_with_parent(self):
        """Test output directory with parent hierarchy."""
        parent_config = {"title": "Parent Module"}
        parent = PageNode("parent", parent_config)

        child_config = {"title": "Child Module"}
        child = PageNode("child", child_config, parent=parent)

        base_dir = Path("/tmp/generated")
        output_dir = child.get_output_dir(base_dir)

        assert output_dir == base_dir / "parent_module"

    def test_get_output_dir_nested_hierarchy(self):
        """Test output directory with multi-level hierarchy."""
        grandparent_config = {"title": "Grandparent"}
        grandparent = PageNode("gp", grandparent_config)

        parent_config = {"title": "Parent"}
        parent = PageNode("parent", parent_config, parent=grandparent)

        child_config = {"title": "Child"}
        child = PageNode("child", child_config, parent=parent)

        base_dir = Path("/tmp/generated")
        output_dir = child.get_output_dir(base_dir)

        assert output_dir == base_dir / "grandparent" / "parent"

    def test_get_output_file(self):
        """Test full output file path generation."""
        config = {"title": "Test Module"}
        node = PageNode("test", config)
        base_dir = Path("/tmp/generated")

        output_file = node.get_output_file(base_dir)
        assert output_file == base_dir / "test_module.rst"

    def test_get_output_file_with_parent(self):
        """Test full output file path with parent."""
        parent_config = {"title": "Parent"}
        parent = PageNode("parent", parent_config)

        child_config = {"title": "Child"}
        child = PageNode("child", child_config, parent=parent)

        base_dir = Path("/tmp/generated")
        output_file = child.get_output_file(base_dir)

        assert output_file == base_dir / "parent" / "child.rst"

    def test_get_relative_path_from(self):
        """Test relative path calculation."""
        config = {"title": "Test Module"}
        node = PageNode("test", config)
        base_dir = Path("/tmp/generated")

        relative_path = node.get_relative_path_from(base_dir, base_dir)
        assert relative_path == "test_module"

    def test_get_relative_path_from_with_parent(self):
        """Test relative path with parent hierarchy."""
        parent_config = {"title": "Parent"}
        parent = PageNode("parent", parent_config)

        child_config = {"title": "Child"}
        child = PageNode("child", child_config, parent=parent)

        base_dir = Path("/tmp/generated")
        parent_dir = parent.get_output_dir(base_dir)

        relative_path = child.get_relative_path_from(parent_dir, base_dir)
        # Child is inside parent directory, so relative path includes parent
        assert "child" in relative_path

    def test_is_leaf_true(self):
        """Test is_leaf returns True for nodes without children."""
        config = {"title": "Leaf Node"}
        node = PageNode("leaf", config)

        assert node.is_leaf() is True

    def test_is_leaf_false(self):
        """Test is_leaf returns False for nodes with children."""
        parent_config = {"title": "Parent"}
        parent = PageNode("parent", parent_config)

        child_config = {"title": "Child"}
        child = PageNode("child", child_config)
        parent.children.append(child)

        assert parent.is_leaf() is False

    def test_has_module_true(self):
        """Test has_module returns True when module is defined."""
        config = {"title": "Module", "module": "test.module"}
        node = PageNode("test", config)

        assert node.has_module() is True

    def test_has_module_false(self):
        """Test has_module returns False when module is not defined."""
        config = {"title": "Module"}
        node = PageNode("test", config)

        assert node.has_module() is False

    def test_path_attribute(self):
        """Test path attribute is set correctly."""
        config = {"title": "Test Module"}
        node = PageNode("test", config)

        assert node.path == Path("test_module")

    def test_relative_path_with_windows_separators(self):
        """Test that relative paths use forward slashes."""
        config = {"title": "Test Module"}
        node = PageNode("test", config)
        base_dir = Path("/tmp/generated")

        relative_path = node.get_relative_path_from(base_dir, base_dir)
        # Should not contain backslashes
        assert "\\" not in relative_path
        assert "/" in relative_path or relative_path == "test_module"
