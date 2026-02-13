#ifndef XML_CODEC_HPP
#define XML_CODEC_HPP

#include "sisl_codec.hpp"
#include <string>
#include <stdexcept>

namespace sisl {

class XmlError : public std::runtime_error {
public:
    explicit XmlError(const std::string& msg);
};

// Convert JSON object to XML string
std::string json_to_xml(const json& j);

// Convert XML string to JSON object
json xml_to_json(const std::string& xml_str);

} // namespace sisl

#endif // XML_CODEC_HPP
