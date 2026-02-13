#include "xml_codec.hpp"
#include <pugixml.hpp>
#include <sstream>
#include <cmath>
#include <limits>

namespace sisl {

XmlError::XmlError(const std::string& msg)
    : std::runtime_error(msg)
{}

namespace {

// Return the XML type name for a JSON value
std::string json_type_name(const json& j) {
    if (j.is_null()) return "null";
    if (j.is_boolean()) return "bool";
    if (j.is_number_integer()) return "int";
    if (j.is_number_float()) return "float";
    if (j.is_string()) return "str";
    if (j.is_array()) return "list";
    if (j.is_object()) return "obj";
    throw XmlError("Unknown JSON type");
}

// Encode a JSON value as the text content of an XML element
std::string encode_value(const json& j) {
    if (j.is_null()) return "";
    if (j.is_boolean()) return j.get<bool>() ? "true" : "false";
    if (j.is_number_integer()) return std::to_string(j.get<int64_t>());
    if (j.is_number_float()) {
        double val = j.get<double>();
        if (std::isnan(val) || std::isinf(val)) {
            throw XmlError("Cannot encode NaN or Infinity in XML");
        }
        std::ostringstream oss;
        oss.precision(std::numeric_limits<double>::max_digits10);
        oss << val;
        std::string str = oss.str();
        if (str.find('.') == std::string::npos &&
            str.find('e') == std::string::npos &&
            str.find('E') == std::string::npos) {
            str += ".0";
        }
        return str;
    }
    if (j.is_string()) return j.get<std::string>();
    throw XmlError("encode_value called on non-scalar type");
}

// Validate that a string is a valid XML element name
// XML names must start with a letter or underscore, followed by letters, digits,
// hyphens, underscores, or periods.
bool is_valid_xml_name(const std::string& name) {
    if (name.empty()) return false;
    char first = name[0];
    if (!(first == '_' || (first >= 'A' && first <= 'Z') || (first >= 'a' && first <= 'z'))) {
        return false;
    }
    for (size_t i = 1; i < name.size(); i++) {
        char c = name[i];
        if (!(c == '_' || c == '-' || c == '.' ||
              (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
              (c >= '0' && c <= '9'))) {
            return false;
        }
    }
    return true;
}

// Build XML DOM nodes from a JSON value, appending to parent
void build_xml_node(pugi::xml_node& parent, const std::string& name, const json& j) {
    if (!is_valid_xml_name(name)) {
        throw XmlError("Invalid XML element name: " + name);
    }
    pugi::xml_node node = parent.append_child(name.c_str());
    node.append_attribute("type").set_value(json_type_name(j).c_str());

    if (j.is_array()) {
        for (const auto& elem : j) {
            build_xml_node(node, "item", elem);
        }
    } else if (j.is_object()) {
        for (auto it = j.begin(); it != j.end(); ++it) {
            build_xml_node(node, it.key(), it.value());
        }
    } else if (j.is_null()) {
        // Self-closing tag, no text content
    } else {
        node.append_child(pugi::node_pcdata).set_value(encode_value(j).c_str());
    }
}

// Decode an XML element into a JSON value using the type attribute
json decode_element(const pugi::xml_node& node) {
    std::string type = node.attribute("type").as_string();
    if (type.empty()) {
        throw XmlError(std::string("Missing type attribute on element: ") + node.name());
    }

    std::string text = node.child_value();

    if (type == "null") {
        return json(nullptr);
    } else if (type == "bool") {
        if (text == "true") return json(true);
        if (text == "false") return json(false);
        throw XmlError("Bool value must be 'true' or 'false', got: " + text);
    } else if (type == "int") {
        try {
            size_t pos = 0;
            int64_t val = std::stoll(text, &pos);
            if (pos != text.size()) {
                throw XmlError("Invalid integer value: " + text);
            }
            return json(val);
        } catch (const XmlError&) {
            throw;
        } catch (...) {
            throw XmlError("Invalid integer value: " + text);
        }
    } else if (type == "float") {
        try {
            size_t pos = 0;
            double val = std::stod(text, &pos);
            if (pos != text.size()) {
                throw XmlError("Invalid float value: " + text);
            }
            return json(val);
        } catch (const XmlError&) {
            throw;
        } catch (...) {
            throw XmlError("Invalid float value: " + text);
        }
    } else if (type == "str") {
        return json(text);
    } else if (type == "list") {
        json arr = json::array();
        for (pugi::xml_node child = node.first_child(); child; child = child.next_sibling()) {
            arr.push_back(decode_element(child));
        }
        return arr;
    } else if (type == "obj") {
        json obj = json::object();
        for (pugi::xml_node child = node.first_child(); child; child = child.next_sibling()) {
            obj[child.name()] = decode_element(child);
        }
        return obj;
    }

    throw XmlError("Unknown type: " + type);
}

// --- Generic XML mode helpers ---

// Check if a parsed XML document uses the typed format (<root> + type attributes)
bool is_typed_xml(const pugi::xml_document& doc) {
    pugi::xml_node root = doc.child("root");
    if (!root) return false;
    for (pugi::xml_node child = root.first_child(); child; child = child.next_sibling()) {
        if (child.type() == pugi::node_element) {
            return !child.attribute("type").empty();
        }
    }
    // Empty <root> — treat as typed (backwards compat)
    return true;
}

// Check if JSON uses the generic representation (_root key present)
bool is_generic_json(const json& j) {
    return j.is_object() && j.contains("_root");
}

// Recursively convert a pugixml element node to generic JSON representation
json parse_generic_element(const pugi::xml_node& node) {
    json elem = json::object();
    elem["_tag"] = std::string(node.name());

    // Attributes (including namespace declarations like xmlns)
    if (node.first_attribute()) {
        json attrs = json::object();
        for (pugi::xml_attribute attr = node.first_attribute(); attr; attr = attr.next_attribute()) {
            attrs[attr.name()] = std::string(attr.value());
        }
        elem["_attrs"] = attrs;
    }

    // Check for child elements
    bool has_child_elements = false;
    for (pugi::xml_node child = node.first_child(); child; child = child.next_sibling()) {
        if (child.type() == pugi::node_element) {
            has_child_elements = true;
            break;
        }
    }

    if (has_child_elements) {
        json children = json::array();
        for (pugi::xml_node child = node.first_child(); child; child = child.next_sibling()) {
            if (child.type() == pugi::node_element) {
                children.push_back(parse_generic_element(child));
            }
        }
        elem["_children"] = children;
    } else {
        // Text-only or empty element
        std::string text = node.child_value();
        if (!text.empty()) {
            elem["_text"] = text;
        }
    }

    return elem;
}

// Convert a generic XML document to JSON
json xml_to_json_generic(const pugi::xml_document& doc) {
    json result = json::object();

    // Capture XML declaration
    for (pugi::xml_node node = doc.first_child(); node; node = node.next_sibling()) {
        if (node.type() == pugi::node_declaration) {
            json decl = json::object();
            for (pugi::xml_attribute attr = node.first_attribute(); attr; attr = attr.next_attribute()) {
                decl[attr.name()] = std::string(attr.value());
            }
            result["_decl"] = decl;
            break;
        }
    }

    // Find first element node as root
    for (pugi::xml_node node = doc.first_child(); node; node = node.next_sibling()) {
        if (node.type() == pugi::node_element) {
            result["_root"] = parse_generic_element(node);
            break;
        }
    }

    return result;
}

// Recursively build pugixml nodes from generic JSON element representation
void build_generic_element(pugi::xml_node& parent, const json& elem) {
    std::string tag = elem.at("_tag").get<std::string>();
    pugi::xml_node node = parent.append_child(tag.c_str());

    if (elem.contains("_attrs")) {
        for (auto it = elem["_attrs"].begin(); it != elem["_attrs"].end(); ++it) {
            node.append_attribute(it.key().c_str()).set_value(it.value().get<std::string>().c_str());
        }
    }

    if (elem.contains("_children")) {
        for (const auto& child : elem["_children"]) {
            build_generic_element(node, child);
        }
    } else if (elem.contains("_text")) {
        node.append_child(pugi::node_pcdata).set_value(elem["_text"].get<std::string>().c_str());
    }
}

// Convert generic JSON representation back to XML string
std::string json_to_xml_generic(const json& j) {
    pugi::xml_document doc;

    // Create declaration from _decl
    if (j.contains("_decl")) {
        pugi::xml_node decl = doc.prepend_child(pugi::node_declaration);
        for (auto it = j["_decl"].begin(); it != j["_decl"].end(); ++it) {
            decl.append_attribute(it.key().c_str()).set_value(it.value().get<std::string>().c_str());
        }
    }

    // Build root element from _root
    if (j.contains("_root")) {
        build_generic_element(doc, j["_root"]);
    }

    std::ostringstream oss;
    doc.save(oss, "\t");
    return oss.str();
}

} // anonymous namespace

std::string json_to_xml(const json& j) {
    if (!j.is_object()) {
        throw XmlError("Top-level value must be a JSON object");
    }

    // Route: generic mode if _root key is present
    if (is_generic_json(j)) {
        return json_to_xml_generic(j);
    }

    // Typed mode (original behavior)
    pugi::xml_document doc;
    pugi::xml_node decl = doc.prepend_child(pugi::node_declaration);
    decl.append_attribute("version").set_value("1.0");
    decl.append_attribute("encoding").set_value("UTF-8");

    pugi::xml_node root = doc.append_child("root");

    for (auto it = j.begin(); it != j.end(); ++it) {
        build_xml_node(root, it.key(), it.value());
    }

    std::ostringstream oss;
    doc.save(oss, "  ");
    return oss.str();
}

json xml_to_json(const std::string& xml_str) {
    pugi::xml_document doc;
    constexpr unsigned int parse_flags =
        (pugi::parse_default & ~pugi::parse_doctype) | pugi::parse_declaration;
    pugi::xml_parse_result result = doc.load_string(xml_str.c_str(), parse_flags);

    if (!result) {
        throw XmlError(std::string("XML parse error: ") + result.description());
    }

    // Route: typed mode if <root> + type attributes, generic otherwise
    if (is_typed_xml(doc)) {
        pugi::xml_node root = doc.child("root");
        json obj = json::object();
        for (pugi::xml_node child = root.first_child(); child; child = child.next_sibling()) {
            obj[child.name()] = decode_element(child);
        }
        return obj;
    }

    return xml_to_json_generic(doc);
}

} // namespace sisl
