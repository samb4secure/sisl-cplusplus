#include "sisl_codec.hpp"
#include "merge.hpp"
#include "split.hpp"
#include "unicode_escape.hpp"
#include <iostream>
#include <sstream>
#include <cstdlib>
#include <optional>

// Exit codes
constexpr int EXIT_SUCCESS_CODE = 0;
constexpr int EXIT_PARSE_ERROR = 2;
constexpr int EXIT_INTERNAL_ERROR = 3;

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " --dumps [--max-length N]\n";
    std::cerr << "       " << prog << " --loads\n";
    std::cerr << "\n";
    std::cerr << "Options:\n";
    std::cerr << "  --dumps         Convert JSON (stdin) to SISL (stdout)\n";
    std::cerr << "  --loads         Convert SISL (stdin) to JSON (stdout)\n";
    std::cerr << "  --max-length N  Split output into parts <= N bytes\n";
}

std::string read_stdin() {
    std::ostringstream ss;
    ss << std::cin.rdbuf();
    return ss.str();
}

int do_dumps(const std::string& input, std::optional<size_t> max_length) {
    try {
        // Parse JSON input
        sisl::json j = sisl::json::parse(input);

        if (!j.is_object()) {
            std::cerr << "Error: Top-level JSON must be an object\n";
            return EXIT_PARSE_ERROR;
        }

        if (max_length) {
            // Try to encode, split if needed
            std::string full = sisl::dumps(j);
            if (full.size() <= *max_length) {
                // Fits in one part
                std::cout << full << "\n";
            } else {
                // Need to split
                auto parts = sisl::split_dumps(j, *max_length);
                if (parts.empty()) {
                    // Shouldn't happen if full.size() > max_length
                    std::cout << full << "\n";
                } else {
                    // Output as JSON array of SISL strings
                    sisl::json arr = sisl::json::array();
                    for (const auto& part : parts) {
                        arr.push_back(part);
                    }
                    std::cout << arr.dump() << "\n";
                }
            }
        } else {
            // No max-length, output single SISL string
            std::cout << sisl::dumps(j) << "\n";
        }

        return EXIT_SUCCESS_CODE;
    } catch (const sisl::json::parse_error& e) {
        std::cerr << "JSON parse error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const sisl::CodecError& e) {
        std::cerr << "Codec error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const std::exception& e) {
        std::cerr << "Internal error: " << e.what() << "\n";
        return EXIT_INTERNAL_ERROR;
    }
}

int do_loads(const std::string& input) {
    try {
        sisl::json result;

        // Try to parse as JSON array first (for joining multiple SISL strings)
        bool is_json_array = false;
        try {
            auto parsed = sisl::json::parse(input);
            if (parsed.is_array()) {
                // Check if all elements are strings
                bool all_strings = true;
                for (const auto& elem : parsed) {
                    if (!elem.is_string()) {
                        all_strings = false;
                        break;
                    }
                }
                if (all_strings && !parsed.empty()) {
                    is_json_array = true;
                    // Extract strings and merge
                    std::vector<std::string> sisl_strings;
                    for (const auto& elem : parsed) {
                        sisl_strings.push_back(elem.get<std::string>());
                    }
                    result = sisl::merge_sisl_strings(sisl_strings);
                }
            }
        } catch (...) {
            // Not valid JSON, treat as raw SISL
        }

        if (!is_json_array) {
            // Parse as single SISL string
            result = sisl::loads(input);
        }

        // Output compact JSON
        std::cout << result.dump() << "\n";
        return EXIT_SUCCESS_CODE;

    } catch (const sisl::ParseError& e) {
        std::cerr << "SISL parse error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const sisl::LexerError& e) {
        std::cerr << "SISL lexer error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const sisl::CodecError& e) {
        std::cerr << "Codec error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const sisl::EscapeError& e) {
        std::cerr << "Escape error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    } catch (const std::exception& e) {
        std::cerr << "Internal error: " << e.what() << "\n";
        return EXIT_INTERNAL_ERROR;
    }
}

int main(int argc, char* argv[]) {
    bool do_dumps_mode = false;
    bool do_loads_mode = false;
    std::optional<size_t> max_length;

    // Parse arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--dumps") {
            do_dumps_mode = true;
        } else if (arg == "--loads") {
            do_loads_mode = true;
        } else if (arg == "--max-length") {
            if (i + 1 >= argc) {
                std::cerr << "Error: --max-length requires a value\n";
                return EXIT_PARSE_ERROR;
            }
            try {
                max_length = std::stoull(argv[++i]);
            } catch (...) {
                std::cerr << "Error: Invalid max-length value\n";
                return EXIT_PARSE_ERROR;
            }
        } else if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return EXIT_SUCCESS_CODE;
        } else {
            std::cerr << "Error: Unknown argument: " << arg << "\n";
            print_usage(argv[0]);
            return EXIT_PARSE_ERROR;
        }
    }

    // Validate arguments
    if (do_dumps_mode && do_loads_mode) {
        std::cerr << "Error: Cannot use both --dumps and --loads\n";
        return EXIT_PARSE_ERROR;
    }

    if (!do_dumps_mode && !do_loads_mode) {
        std::cerr << "Error: Must specify --dumps or --loads\n";
        print_usage(argv[0]);
        return EXIT_PARSE_ERROR;
    }

    if (max_length && !do_dumps_mode) {
        std::cerr << "Error: --max-length can only be used with --dumps\n";
        return EXIT_PARSE_ERROR;
    }

    // Read stdin
    std::string input = read_stdin();

    // Execute
    if (do_dumps_mode) {
        return do_dumps(input, max_length);
    } else {
        return do_loads(input);
    }
}
