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

} // anonymous namespace

std::string json_to_xml(const json& j) {
    if (!j.is_object()) {
        throw XmlError("Top-level value must be a JSON object");
    }

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
    constexpr unsigned int parse_flags = pugi::parse_default & ~pugi::parse_doctype;
    pugi::xml_parse_result result = doc.load_string(xml_str.c_str(), parse_flags);

    if (!result) {
        throw XmlError(std::string("XML parse error: ") + result.description());
    }

    pugi::xml_node root = doc.child("root");
    if (!root) {
        throw XmlError("Missing <root> element");
    }

    json obj = json::object();
    for (pugi::xml_node child = root.first_child(); child; child = child.next_sibling()) {
        obj[child.name()] = decode_element(child);
    }
    return obj;
}

} // namespace sisl
