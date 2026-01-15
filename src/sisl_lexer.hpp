#ifndef SISL_LEXER_HPP
#define SISL_LEXER_HPP

#include <string>
#include <string_view>
#include <variant>
#include <stdexcept>

namespace sisl {

enum class TokenType {
    LBRACE,      // {
    RBRACE,      // }
    COLON,       // :
    COMMA,       // ,
    BANG,        // !
    STRING,      // "..."
    NAME,        // identifier (name or type)
    END_OF_INPUT
};

struct Token {
    TokenType type;
    std::string value;
    size_t line;
    size_t column;
};

class LexerError : public std::runtime_error {
public:
    LexerError(const std::string& msg, size_t line, size_t column);
    size_t line() const { return line_; }
    size_t column() const { return column_; }
private:
    size_t line_;
    size_t column_;
};

class Lexer {
public:
    explicit Lexer(std::string_view input);

    Token next_token();
    Token peek_token();

    size_t current_line() const { return line_; }
    size_t current_column() const { return column_; }

private:
    void advance();
    char current() const;
    char peek() const;
    bool at_end() const;

    void skip_whitespace();
    Token scan_string();
    Token scan_name();

    bool is_name_start(char c) const;
    bool is_name_char(char c) const;
    bool is_whitespace(char c) const;

    std::string_view input_;
    size_t pos_ = 0;
    size_t line_ = 1;
    size_t column_ = 1;

    bool has_peeked_ = false;
    Token peeked_token_;
};

} // namespace sisl

#endif // SISL_LEXER_HPP
