#include "split.hpp"
#include <stdexcept>

namespace sisl {

namespace {

// A path component is either a string (object key) or size_t (array index)
struct PathComponent {
    bool is_index;
    std::string key;
    size_t index;

    PathComponent(const std::string& k) : is_index(false), key(k), index(0) {}
    PathComponent(size_t i) : is_index(true), key(""), index(i) {}
};

using Path = std::vector<PathComponent>;

// Leaf: a path to a primitive value
struct Leaf {
    Path path;
    json value;
};

// Collect all leaves (primitives) from a JSON value
void collect_leaves(const json& j, const Path& current_path, std::vector<Leaf>& leaves) {
    if (j.is_object()) {
        for (auto it = j.begin(); it != j.end(); ++it) {
            Path new_path = current_path;
            new_path.emplace_back(it.key());
            collect_leaves(it.value(), new_path, leaves);
        }
    } else if (j.is_array()) {
        size_t idx = 0;
        for (const auto& elem : j) {
            Path new_path = current_path;
            new_path.emplace_back(idx);
            collect_leaves(elem, new_path, leaves);
            idx++;
        }
    } else {
        // Primitive
        leaves.push_back(Leaf{current_path, j});
    }
}

// Build a JSON fragment from a leaf (adds structural scaffolding)
json build_fragment(const Leaf& leaf) {
    if (leaf.path.empty()) {
        return leaf.value;
    }

    // Build from inside out
    json current = leaf.value;

    for (auto it = leaf.path.rbegin(); it != leaf.path.rend(); ++it) {
        if (it->is_index) {
            // Wrap in object with _N key (SISL list representation)
            json wrapper = json::object();
            wrapper["_" + std::to_string(it->index)] = current;
            current = wrapper;
        } else {
            // Wrap in object with key
            json wrapper = json::object();
            wrapper[it->key] = current;
            current = wrapper;
        }
    }

    return current;
}

} // anonymous namespace

std::vector<std::string> split_dumps(const json& j, size_t max_length) {
    // First, try the full encoding
    std::string full = dumps(j);
    if (full.size() <= max_length) {
        return {}; // No split needed
    }

    // Collect all leaves
    std::vector<Leaf> leaves;
    collect_leaves(j, {}, leaves);

    if (leaves.empty()) {
        // Empty object
        return {"{}"};
    }

    // Build fragments and encode each
    std::vector<std::pair<json, std::string>> fragments;
    for (const auto& leaf : leaves) {
        json frag = build_fragment(leaf);
        std::string encoded = dumps(frag);
        if (encoded.size() > max_length) {
            throw CodecError("max-length too small to encode any fragment (minimum needed: " +
                std::to_string(encoded.size()) + " bytes)");
        }
        fragments.emplace_back(frag, encoded);
    }

    // Greedy packing: combine fragments that fit together
    std::vector<std::string> result;

    size_t i = 0;
    while (i < fragments.size()) {
        // Start with first unpacked fragment
        json combined = fragments[i].first;
        std::string current_encoded = fragments[i].second;
        i++;

        // Try to add more fragments
        while (i < fragments.size()) {
            // Try combining
            json test_combined = combined;

            // Merge the fragment into test_combined
            // Simple merge for top-level objects
            const auto& next_frag = fragments[i].first;
            for (auto it = next_frag.begin(); it != next_frag.end(); ++it) {
                if (test_combined.contains(it.key())) {
                    // Need to merge nested structures
                    // For simplicity, we'll just encode separately
                    break;
                }
                test_combined[it.key()] = it.value();
            }

            std::string test_encoded = dumps(test_combined);
            if (test_encoded.size() <= max_length) {
                combined = test_combined;
                current_encoded = test_encoded;
                i++;
            } else {
                break;
            }
        }

        result.push_back(current_encoded);
    }

    return result;
}

} // namespace sisl
