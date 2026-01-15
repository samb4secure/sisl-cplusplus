#ifndef UNICODE_ESCAPE_HPP
#define UNICODE_ESCAPE_HPP

#include <string>
#include <stdexcept>

namespace sisl {

class EscapeError : public std::runtime_error {
public:
    explicit EscapeError(const std::string& msg);
};

// Unescape a SISL string value (process escape sequences)
// Input is the raw string content from lexer (already without surrounding quotes)
std::string unescape_sisl_string(const std::string& input);

// Escape a string for SISL output (add escape sequences where needed)
std::string escape_sisl_string(const std::string& input);

} // namespace sisl

#endif // UNICODE_ESCAPE_HPP
