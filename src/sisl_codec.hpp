#ifndef SISL_CODEC_HPP
#define SISL_CODEC_HPP

#include "sisl_parser.hpp"
#include <nlohmann/json.hpp>
#include <string>
#include <stdexcept>

namespace sisl {

// Use ordered_json to preserve key order
using json = nlohmann::ordered_json;

class CodecError : public std::runtime_error {
public:
    explicit CodecError(const std::string& msg);
};

// Convert JSON to canonical SISL string
std::string json_to_sisl(const json& j);

// Convert SISL AST to JSON
json sisl_to_json(const std::shared_ptr<Grouping>& grouping);

// Parse SISL string and convert to JSON
json loads(const std::string& sisl_str);

// Convert JSON to SISL string (wrapper around json_to_sisl)
std::string dumps(const json& j);

} // namespace sisl

#endif // SISL_CODEC_HPP
