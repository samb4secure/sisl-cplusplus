#ifndef SISL_PARSER_HPP
#define SISL_PARSER_HPP

#include "sisl_lexer.hpp"
#include <string>
#include <vector>
#include <memory>
#include <variant>
#include <stdexcept>

namespace sisl {

// AST node types
struct StringValue;
struct Grouping;

using Value = std::variant<StringValue, std::shared_ptr<Grouping>>;

struct StringValue {
    std::string content;
};

struct Element {
    std::string name;
    std::string type;
    Value value;
};

struct Grouping {
    std::vector<Element> elements;
};

class ParseError : public std::runtime_error {
public:
    ParseError(const std::string& msg, size_t line, size_t column);
    size_t line() const { return line_; }
    size_t column() const { return column_; }
private:
    size_t line_;
    size_t column_;
};

class Parser {
public:
    explicit Parser(std::string_view input);

    std::shared_ptr<Grouping> parse();

private:
    Token expect(TokenType type, const std::string& what);
    Token consume();
    Token peek();

    std::shared_ptr<Grouping> parse_grouping();
    Element parse_element();
    Value parse_value();

    Lexer lexer_;
};

} // namespace sisl

#endif // SISL_PARSER_HPP
