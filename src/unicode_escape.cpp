#include "unicode_escape.hpp"
#include <sstream>
#include <iomanip>

namespace sisl {

EscapeError::EscapeError(const std::string& msg)
    : std::runtime_error(msg)
{}

namespace {

bool is_hex_digit(char c) {
    return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
}

int hex_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return 0;
}

// Convert a Unicode codepoint to UTF-8
std::string codepoint_to_utf8(uint32_t cp) {
    std::string result;
    if (cp < 0x80) {
        result += static_cast<char>(cp);
    } else if (cp < 0x800) {
        result += static_cast<char>(0xC0 | (cp >> 6));
        result += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x10000) {
        result += static_cast<char>(0xE0 | (cp >> 12));
        result += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        result += static_cast<char>(0x80 | (cp & 0x3F));
    } else if (cp < 0x110000) {
        result += static_cast<char>(0xF0 | (cp >> 18));
        result += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
        result += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
        result += static_cast<char>(0x80 | (cp & 0x3F));
    } else {
        throw EscapeError("Invalid Unicode codepoint");
    }
    return result;
}

uint32_t parse_hex(const std::string& input, size_t& pos, size_t count) {
    uint32_t value = 0;
    for (size_t i = 0; i < count; i++) {
        if (pos >= input.size() || !is_hex_digit(input[pos])) {
            throw EscapeError("Invalid hex escape sequence");
        }
        value = (value << 4) | hex_value(input[pos]);
        pos++;
    }
    return value;
}

} // anonymous namespace

std::string unescape_sisl_string(const std::string& input) {
    std::string result;
    size_t pos = 0;

    while (pos < input.size()) {
        if (input[pos] == '\\' && pos + 1 < input.size()) {
            pos++; // skip backslash
            char c = input[pos];
            pos++;

            switch (c) {
                case '"':
                    result += '"';
                    break;
                case '\\':
                    result += '\\';
                    break;
                case 'r':
                    result += '\r';
                    break;
                case 't':
                    result += '\t';
                    break;
                case 'n':
                    result += '\n';
                    break;
                case 'x': {
                    // \xHH - 2 hex digits
                    uint32_t value = parse_hex(input, pos, 2);
                    result += static_cast<char>(value);
                    break;
                }
                case 'u': {
                    // \uHHHH - 4 hex digits
                    uint32_t value = parse_hex(input, pos, 4);
                    result += codepoint_to_utf8(value);
                    break;
                }
                case 'U': {
                    // \UHHHHHHHH - 8 hex digits
                    uint32_t value = parse_hex(input, pos, 8);
                    result += codepoint_to_utf8(value);
                    break;
                }
                default:
                    throw EscapeError(std::string("Invalid escape sequence: \\") + c);
            }
        } else {
            result += input[pos];
            pos++;
        }
    }

    return result;
}

std::string escape_sisl_string(const std::string& input) {
    std::string result;

    for (unsigned char c : input) {
        switch (c) {
            case '"':
                result += "\\\"";
                break;
            case '\\':
                result += "\\\\";
                break;
            case '\r':
                result += "\\r";
                break;
            case '\t':
                result += "\\t";
                break;
            case '\n':
                result += "\\n";
                break;
            default:
                // Printable ASCII (0x20-0x7E, excluding " and \)
                if (c >= 0x20 && c <= 0x7E) {
                    result += c;
                } else {
                    // Use \xHH for non-printable bytes
                    std::ostringstream oss;
                    oss << "\\x" << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(c);
                    result += oss.str();
                }
                break;
        }
    }

    return result;
}

} // namespace sisl
