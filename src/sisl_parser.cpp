#include "sisl_parser.hpp"

namespace sisl {

ParseError::ParseError(const std::string& msg, size_t line, size_t column)
    : std::runtime_error(msg + " at line " + std::to_string(line) + ", column " + std::to_string(column))
    , line_(line)
    , column_(column)
{}

Parser::Parser(std::string_view input)
    : lexer_(input)
{}

Token Parser::consume() {
    return lexer_.next_token();
}

Token Parser::peek() {
    return lexer_.peek_token();
}

Token Parser::expect(TokenType type, const std::string& what) {
    Token tok = consume();
    if (tok.type != type) {
        throw ParseError("Expected " + what + ", got '" + tok.value + "'", tok.line, tok.column);
    }
    return tok;
}

std::shared_ptr<Grouping> Parser::parse() {
    auto grouping = parse_grouping();

    // Skip trailing whitespace and check for end of input
    Token tok = peek();
    if (tok.type != TokenType::END_OF_INPUT) {
        throw ParseError("Unexpected token after grouping: '" + tok.value + "'", tok.line, tok.column);
    }

    return grouping;
}

std::shared_ptr<Grouping> Parser::parse_grouping() {
    expect(TokenType::LBRACE, "'{'");

    auto grouping = std::make_shared<Grouping>();

    // Check for empty grouping
    if (peek().type == TokenType::RBRACE) {
        consume();
        return grouping;
    }

    // Parse first element
    grouping->elements.push_back(parse_element());

    // Parse remaining elements
    while (peek().type == TokenType::COMMA) {
        consume(); // eat comma
        // Check for trailing comma (allowed or not?)
        if (peek().type == TokenType::RBRACE) {
            break;
        }
        grouping->elements.push_back(parse_element());
    }

    expect(TokenType::RBRACE, "'}'");
    return grouping;
}

Element Parser::parse_element() {
    Element elem;

    // Parse name
    Token name_tok = expect(TokenType::NAME, "element name");
    elem.name = name_tok.value;

    // Parse ':'
    expect(TokenType::COLON, "':'");

    // Parse '!'
    expect(TokenType::BANG, "'!'");

    // Parse type
    Token type_tok = expect(TokenType::NAME, "type name");
    elem.type = type_tok.value;

    // Parse value
    elem.value = parse_value();

    return elem;
}

Value Parser::parse_value() {
    Token tok = peek();

    if (tok.type == TokenType::STRING) {
        consume();
        return StringValue{tok.value};
    } else if (tok.type == TokenType::LBRACE) {
        return parse_grouping();
    } else {
        throw ParseError("Expected string or grouping, got '" + tok.value + "'", tok.line, tok.column);
    }
}

} // namespace sisl
