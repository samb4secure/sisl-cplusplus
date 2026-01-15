#include "merge.hpp"
#include "unicode_escape.hpp"
#include <map>
#include <algorithm>

namespace sisl {

namespace {

// Mergeable representation that preserves sparse list indices
struct MergeableValue;

using MergeablePtr = std::shared_ptr<MergeableValue>;
using IndexMap = std::map<size_t, MergeablePtr>;

struct MergeableValue {
    enum class Type { OBJECT, LIST, PRIMITIVE };
    Type type;

    // For objects: ordered vector of key-value pairs
    std::vector<std::pair<std::string, MergeablePtr>> obj_entries;

    // For lists: sparse index map (does NOT fill gaps)
    IndexMap list_entries;

    // For primitives: the JSON value
    json primitive;
};

// Forward declarations
MergeablePtr from_element(const Element& elem);
MergeablePtr from_grouping_as_object(const std::shared_ptr<Grouping>& grouping);
json to_json(const MergeablePtr& mv);

// Convert a SISL Element value to MergeableValue
MergeablePtr from_element(const Element& elem) {
    auto mv = std::make_shared<MergeableValue>();

    if (std::holds_alternative<StringValue>(elem.value)) {
        // Primitive value
        const auto& raw_value = std::get<StringValue>(elem.value).content;
        std::string value = unescape_sisl_string(raw_value);

        mv->type = MergeableValue::Type::PRIMITIVE;

        if (elem.type == "null") {
            mv->primitive = json(nullptr);
        } else if (elem.type == "bool") {
            mv->primitive = (value == "true");
        } else if (elem.type == "int") {
            mv->primitive = std::stoll(value);
        } else if (elem.type == "float") {
            mv->primitive = std::stod(value);
        } else if (elem.type == "str") {
            mv->primitive = value;
        } else {
            throw CodecError("Unknown type: " + elem.type);
        }
    } else {
        // Grouping value (obj or list)
        auto grouping = std::get<std::shared_ptr<Grouping>>(elem.value);

        if (elem.type == "obj") {
            mv->type = MergeableValue::Type::OBJECT;
            for (const auto& e : grouping->elements) {
                mv->obj_entries.emplace_back(e.name, from_element(e));
            }
        } else if (elem.type == "list") {
            mv->type = MergeableValue::Type::LIST;
            for (const auto& e : grouping->elements) {
                // Extract index from _N name
                if (e.name.empty() || e.name[0] != '_') {
                    throw CodecError("Invalid list element name: " + e.name);
                }
                size_t idx = std::stoull(e.name.substr(1));
                mv->list_entries[idx] = from_element(e);
            }
        } else {
            throw CodecError("Unknown grouping type: " + elem.type);
        }
    }

    return mv;
}

// Convert a top-level grouping to MergeableValue (as object)
MergeablePtr from_grouping_as_object(const std::shared_ptr<Grouping>& grouping) {
    auto mv = std::make_shared<MergeableValue>();
    mv->type = MergeableValue::Type::OBJECT;
    for (const auto& e : grouping->elements) {
        mv->obj_entries.emplace_back(e.name, from_element(e));
    }
    return mv;
}

// Merge two MergeableValues
MergeablePtr merge_values(const MergeablePtr& a, const MergeablePtr& b) {
    if (a->type != b->type) {
        throw CodecError("Type conflict during merge");
    }

    auto result = std::make_shared<MergeableValue>();
    result->type = a->type;

    switch (a->type) {
        case MergeableValue::Type::OBJECT: {
            // Start with A's entries
            result->obj_entries = a->obj_entries;

            // Merge B's entries
            for (const auto& entry : b->obj_entries) {
                const std::string& key = entry.first;
                const auto& bval = entry.second;

                // Check if key exists in result
                auto it = std::find_if(result->obj_entries.begin(), result->obj_entries.end(),
                    [&key](const auto& p) { return p.first == key; });

                if (it != result->obj_entries.end()) {
                    // Key exists - merge recursively
                    it->second = merge_values(it->second, bval);
                } else {
                    // Key doesn't exist - append
                    result->obj_entries.emplace_back(key, bval);
                }
            }
            break;
        }
        case MergeableValue::Type::LIST: {
            // Start with A's entries
            result->list_entries = a->list_entries;

            // Merge B's entries
            for (const auto& entry : b->list_entries) {
                size_t idx = entry.first;
                const auto& bval = entry.second;

                auto it = result->list_entries.find(idx);
                if (it != result->list_entries.end()) {
                    // Index exists - merge recursively
                    it->second = merge_values(it->second, bval);
                } else {
                    // Index doesn't exist - add
                    result->list_entries[idx] = bval;
                }
            }
            break;
        }
        case MergeableValue::Type::PRIMITIVE:
            // For primitives, B overwrites A
            result->primitive = b->primitive;
            break;
    }

    return result;
}

// Convert MergeableValue to JSON (filling gaps with null for lists)
json to_json(const MergeablePtr& mv) {
    switch (mv->type) {
        case MergeableValue::Type::OBJECT: {
            json obj = json::object();
            for (const auto& entry : mv->obj_entries) {
                obj[entry.first] = to_json(entry.second);
            }
            return obj;
        }
        case MergeableValue::Type::LIST: {
            if (mv->list_entries.empty()) {
                return json::array();
            }
            // Find max index
            size_t max_idx = mv->list_entries.rbegin()->first;
            json arr = json::array();
            for (size_t i = 0; i <= max_idx; i++) {
                auto it = mv->list_entries.find(i);
                if (it != mv->list_entries.end()) {
                    arr.push_back(to_json(it->second));
                } else {
                    arr.push_back(json(nullptr));
                }
            }
            return arr;
        }
        case MergeableValue::Type::PRIMITIVE:
            return mv->primitive;
    }
    return json(nullptr);
}

} // anonymous namespace

json merge_sisl_strings(const std::vector<std::string>& sisl_strings) {
    if (sisl_strings.empty()) {
        return json::object();
    }

    // Parse first SISL string to AST, then to MergeableValue
    Parser parser1(sisl_strings[0]);
    auto grouping1 = parser1.parse();
    auto result = from_grouping_as_object(grouping1);

    // Merge remaining
    for (size_t i = 1; i < sisl_strings.size(); i++) {
        Parser parser(sisl_strings[i]);
        auto grouping = parser.parse();
        auto parsed = from_grouping_as_object(grouping);
        result = merge_values(result, parsed);
    }

    return to_json(result);
}

} // namespace sisl
