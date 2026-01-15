#include "sisl_lexer.hpp"

namespace sisl {

LexerError::LexerError(const std::string& msg, size_t line, size_t column)
    : std::runtime_error(msg + " at line " + std::to_string(line) + ", column " + std::to_string(column))
    , line_(line)
    , column_(column)
{}

Lexer::Lexer(std::string_view input)
    : input_(input)
{}

void Lexer::advance() {
    if (pos_ < input_.size()) {
        if (input_[pos_] == '\n') {
            line_++;
            column_ = 1;
        } else {
            column_++;
        }
        pos_++;
    }
}

char Lexer::current() const {
    return pos_ < input_.size() ? input_[pos_] : '\0';
}

char Lexer::peek() const {
    return (pos_ + 1) < input_.size() ? input_[pos_ + 1] : '\0';
}

bool Lexer::at_end() const {
    return pos_ >= input_.size();
}

bool Lexer::is_whitespace(char c) const {
    return c == ' ' || c == '\t' || c == '\r' || c == '\n';
}

bool Lexer::is_name_start(char c) const {
    return c == '_' || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z');
}

bool Lexer::is_name_char(char c) const {
    return is_name_start(c) || c == '-' || c == '.' || (c >= '0' && c <= '9');
}

void Lexer::skip_whitespace() {
    while (!at_end() && is_whitespace(current())) {
        advance();
    }
}

Token Lexer::scan_string() {
    size_t start_line = line_;
    size_t start_col = column_;

    advance(); // skip opening quote

    std::string value;
    while (!at_end() && current() != '"') {
        if (current() == '\\') {
            advance();
            if (at_end()) {
                throw LexerError("Unexpected end of input in escape sequence", line_, column_);
            }
            // Store the raw escape sequence - let unicode_escape handle it
            value += '\\';
            value += current();

            // Handle hex escapes that need more characters
            if (current() == 'x') {
                advance();
                for (int i = 0; i < 2 && !at_end() && current() != '"'; i++) {
                    value += current();
                    advance();
                }
                continue;
            } else if (current() == 'u') {
                advance();
                for (int i = 0; i < 4 && !at_end() && current() != '"'; i++) {
                    value += current();
                    advance();
                }
                continue;
            } else if (current() == 'U') {
                advance();
                for (int i = 0; i < 8 && !at_end() && current() != '"'; i++) {
                    value += current();
                    advance();
                }
                continue;
            }
        } else {
            value += current();
        }
        advance();
    }

    if (at_end()) {
        throw LexerError("Unterminated string", start_line, start_col);
    }

    advance(); // skip closing quote

    return Token{TokenType::STRING, value, start_line, start_col};
}

Token Lexer::scan_name() {
    size_t start_line = line_;
    size_t start_col = column_;

    std::string value;
    while (!at_end() && is_name_char(current())) {
        value += current();
        advance();
    }

    return Token{TokenType::NAME, value, start_line, start_col};
}

Token Lexer::next_token() {
    if (has_peeked_) {
        has_peeked_ = false;
        return peeked_token_;
    }

    skip_whitespace();

    if (at_end()) {
        return Token{TokenType::END_OF_INPUT, "", line_, column_};
    }

    size_t start_line = line_;
    size_t start_col = column_;
    char c = current();

    switch (c) {
        case '{':
            advance();
            return Token{TokenType::LBRACE, "{", start_line, start_col};
        case '}':
            advance();
            return Token{TokenType::RBRACE, "}", start_line, start_col};
        case ':':
            advance();
            return Token{TokenType::COLON, ":", start_line, start_col};
        case ',':
            advance();
            return Token{TokenType::COMMA, ",", start_line, start_col};
        case '!':
            advance();
            return Token{TokenType::BANG, "!", start_line, start_col};
        case '"':
            return scan_string();
        default:
            if (is_name_start(c)) {
                return scan_name();
            }
            throw LexerError(std::string("Unexpected character '") + c + "'", line_, column_);
    }
}

Token Lexer::peek_token() {
    if (!has_peeked_) {
        peeked_token_ = next_token();
        has_peeked_ = true;
    }
    return peeked_token_;
}

} // namespace sisl
