#ifndef MERGE_HPP
#define MERGE_HPP

#include "sisl_codec.hpp"
#include "sisl_parser.hpp"
#include <vector>
#include <string>

namespace sisl {

// Merge multiple SISL strings into a single JSON object
// Implements the joining behavior described in pysisl documentation
json merge_sisl_strings(const std::vector<std::string>& sisl_strings);

} // namespace sisl

#endif // MERGE_HPP
