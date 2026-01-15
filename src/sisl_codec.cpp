#include "sisl_codec.hpp"
#include "unicode_escape.hpp"
#include <sstream>
#include <cmath>
#include <limits>
#include <algorithm>

namespace sisl {

CodecError::CodecError(const std::string& msg)
    : std::runtime_error(msg)
{}

namespace {

// Forward declarations
std::string encode_value(const json& j);
json decode_element(const Element& elem);

// Encode a JSON value to SISL type and value string
std::pair<std::string, std::string> get_type_and_value(const json& j) {
    if (j.is_null()) {
        return {"null", "\"\""};
    } else if (j.is_boolean()) {
        return {"bool", j.get<bool>() ? "\"true\"" : "\"false\""};
    } else if (j.is_number_integer()) {
        return {"int", "\"" + std::to_string(j.get<int64_t>()) + "\""};
    } else if (j.is_number_float()) {
        double val = j.get<double>();
        if (std::isnan(val) || std::isinf(val)) {
            throw CodecError("JSON does not support NaN or Infinity");
        }
        std::ostringstream oss;
        oss.precision(std::numeric_limits<double>::max_digits10);
        oss << val;
        std::string str = oss.str();
        // Ensure it has a decimal point or exponent to be recognized as float
        if (str.find('.') == std::string::npos && str.find('e') == std::string::npos && str.find('E') == std::string::npos) {
            str += ".0";
        }
        return {"float", "\"" + str + "\""};
    } else if (j.is_string()) {
        return {"str", "\"" + escape_sisl_string(j.get<std::string>()) + "\""};
    } else if (j.is_array()) {
        // Arrays are encoded as !list {_0: ..., _1: ..., ...}
        std::ostringstream oss;
        oss << "{";
        bool first = true;
        size_t idx = 0;
        for (const auto& elem : j) {
            if (!first) oss << ", ";
            first = false;
            oss << "_" << idx << ": " << encode_value(elem);
            idx++;
        }
        oss << "}";
        return {"list", oss.str()};
    } else if (j.is_object()) {
        // Objects are encoded as !obj {...}
        std::ostringstream oss;
        oss << "{";
        bool first = true;
        for (auto it = j.begin(); it != j.end(); ++it) {
            if (!first) oss << ", ";
            first = false;
            oss << it.key() << ": " << encode_value(it.value());
        }
        oss << "}";
        return {"obj", oss.str()};
    }

    throw CodecError("Unknown JSON type");
}

// Encode a JSON value to full SISL element value (type + value)
std::string encode_value(const json& j) {
    auto [type, value] = get_type_and_value(j);
    return "!" + type + " " + value;
}

// Decode a SISL string value to JSON based on type
json decode_string_value(const std::string& type, const std::string& raw_value) {
    std::string value = unescape_sisl_string(raw_value);

    if (type == "null") {
        if (!value.empty()) {
            throw CodecError("null value must be empty string");
        }
        return json(nullptr);
    } else if (type == "bool") {
        if (value == "true") return json(true);
        if (value == "false") return json(false);
        throw CodecError("bool value must be 'true' or 'false'");
    } else if (type == "int") {
        try {
            return json(std::stoll(value));
        } catch (...) {
            throw CodecError("Invalid integer value: " + value);
        }
    } else if (type == "float") {
        try {
            return json(std::stod(value));
        } catch (...) {
            throw CodecError("Invalid float value: " + value);
        }
    } else if (type == "str") {
        return json(value);
    }

    throw CodecError("Unknown type for string value: " + type);
}

// Decode a SISL grouping value (for obj or list types)
json decode_grouping_value(const std::string& type, const std::shared_ptr<Grouping>& grouping) {
    if (type == "obj") {
        json obj = json::object();
        for (const auto& elem : grouping->elements) {
            obj[elem.name] = decode_element(elem);
        }
        return obj;
    } else if (type == "list") {
        // Parse list indices and build array
        std::vector<std::pair<size_t, json>> items;
        for (const auto& elem : grouping->elements) {
            // List elements have names like _0, _1, _2, ...
            if (elem.name.empty() || elem.name[0] != '_') {
                throw CodecError("List element name must start with '_': " + elem.name);
            }
            size_t index;
            try {
                index = std::stoull(elem.name.substr(1));
            } catch (...) {
                throw CodecError("Invalid list index: " + elem.name);
            }
            items.emplace_back(index, decode_element(elem));
        }

        // Sort by index
        std::sort(items.begin(), items.end(),
            [](const auto& a, const auto& b) { return a.first < b.first; });

        // Build array, filling gaps with null
        json arr = json::array();
        size_t expected = 0;
        for (const auto& [idx, val] : items) {
            while (expected < idx) {
                arr.push_back(json(nullptr));
                expected++;
            }
            arr.push_back(val);
            expected++;
        }
        return arr;
    }

    throw CodecError("Unknown type for grouping value: " + type);
}

// Decode a single SISL element to JSON value
json decode_element(const Element& elem) {
    if (std::holds_alternative<StringValue>(elem.value)) {
        return decode_string_value(elem.type, std::get<StringValue>(elem.value).content);
    } else {
        auto grouping = std::get<std::shared_ptr<Grouping>>(elem.value);
        return decode_grouping_value(elem.type, grouping);
    }
}

} // anonymous namespace

std::string json_to_sisl(const json& j) {
    if (!j.is_object()) {
        throw CodecError("Top-level SISL must be an object");
    }

    std::ostringstream oss;
    oss << "{";
    bool first = true;
    for (auto it = j.begin(); it != j.end(); ++it) {
        if (!first) oss << ", ";
        first = false;
        oss << it.key() << ": " << encode_value(it.value());
    }
    oss << "}";
    return oss.str();
}

json sisl_to_json(const std::shared_ptr<Grouping>& grouping) {
    json obj = json::object();
    for (const auto& elem : grouping->elements) {
        obj[elem.name] = decode_element(elem);
    }
    return obj;
}

json loads(const std::string& sisl_str) {
    Parser parser(sisl_str);
    auto grouping = parser.parse();
    return sisl_to_json(grouping);
}

std::string dumps(const json& j) {
    return json_to_sisl(j);
}

} // namespace sisl
