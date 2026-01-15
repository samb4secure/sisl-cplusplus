#ifndef SPLIT_HPP
#define SPLIT_HPP

#include "sisl_codec.hpp"
#include <vector>
#include <string>
#include <optional>

namespace sisl {

// Split a JSON object into multiple SISL strings, each <= max_length bytes
// Returns empty vector if the full encoding fits within max_length
// Throws if max_length is too small for any single fragment
std::vector<std::string> split_dumps(const json& j, size_t max_length);

} // namespace sisl

#endif // SPLIT_HPP
