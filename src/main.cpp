#include "sisl_codec.hpp"
#include "xml_codec.hpp"
#include "merge.hpp"
#include "split.hpp"
#include "unicode_escape.hpp"
#include <iostream>
#include <fstream>
#include <sstream>
#include <cstdlib>
#include <cstdio>
#include <optional>

// Exit codes
constexpr int EXIT_SUCCESS_CODE = 0;
constexpr int EXIT_PARSE_ERROR = 2;
constexpr int EXIT_INTERNAL_ERROR = 3;

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog << " --dumps [--xml] [--max-length N] [--input FILE] [--output FILE]\n";
    std::cerr << "       " << prog << " --loads [--xml] [--input FILE] [--output FILE]\n";
    std::cerr << "\n";
    std::cerr << "Options:\n";
    std::cerr << "  --dumps          Convert JSON (stdin) to SISL (stdout)\n";
    std::cerr << "  --loads          Convert SISL (stdin) to JSON (stdout)\n";
    std::cerr << "  --xml            Use XML instead of JSON as the alternate format\n";
    std::cerr << "  --max-length N   Split output into parts <= N bytes\n";
    std::cerr << "  --input FILE     Read input from FILE instead of stdin\n";
    std::cerr << "  --output FILE    Write output to FILE instead of stdout\n";
}

std::string read_input(const std::string& input_file) {
    std::ostringstream ss;
    if (input_file.empty()) {
        ss << std::cin.rdbuf();
    } else {
        std::ifstream ifs(input_file);
        if (!ifs) {
            throw std::runtime_error("Cannot open input file: " + input_file);
        }
        ss << ifs.rdbuf();
    }
    return ss.str();
}

int do_dumps(const std::string& input, std::optional<size_t> max_length, bool xml_mode) {
    try {
        // Parse input (JSON or XML)
        sisl::json j = xml_mode ? sisl::xml_to_json(input) : sisl::json::parse(input);

        if (!j.is_object()) {
            std::cerr << "Error: Top-level input must be an object\n";
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
    } catch (const sisl::XmlError& e) {
        std::cerr << "XML error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
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

int do_loads(const std::string& input, bool xml_mode) {
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

        // Output result
        if (xml_mode) {
            std::cout << sisl::json_to_xml(result);
        } else {
            std::cout << result.dump() << "\n";
        }
        return EXIT_SUCCESS_CODE;

    } catch (const sisl::XmlError& e) {
        std::cerr << "XML error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
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
    bool xml_mode = false;
    std::optional<size_t> max_length;
    std::string input_file;
    std::string output_file;

    // Parse arguments
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        if (arg == "--dumps") {
            do_dumps_mode = true;
        } else if (arg == "--loads") {
            do_loads_mode = true;
        } else if (arg == "--xml") {
            xml_mode = true;
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
        } else if (arg == "--input") {
            if (i + 1 >= argc) {
                std::cerr << "Error: --input requires a file path\n";
                return EXIT_PARSE_ERROR;
            }
            input_file = argv[++i];
        } else if (arg == "--output") {
            if (i + 1 >= argc) {
                std::cerr << "Error: --output requires a file path\n";
                return EXIT_PARSE_ERROR;
            }
            output_file = argv[++i];
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

    // Read input
    std::string input;
    try {
        input = read_input(input_file);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return EXIT_PARSE_ERROR;
    }

    // Set up output redirection.
    // Write to a temp file first so that on failure the target isn't truncated.
    std::ofstream ofs;
    std::streambuf* orig_cout = nullptr;
    std::string tmp_path;
    if (!output_file.empty()) {
        tmp_path = output_file + ".tmp";
        ofs.open(tmp_path);
        if (!ofs) {
            std::cerr << "Error: Cannot open output file: " << output_file << "\n";
            return EXIT_PARSE_ERROR;
        }
        orig_cout = std::cout.rdbuf(ofs.rdbuf());
    }

    // Execute
    int rc;
    if (do_dumps_mode) {
        rc = do_dumps(input, max_length, xml_mode);
    } else {
        rc = do_loads(input, xml_mode);
    }

    // Restore stdout and finalize output file
    if (orig_cout) {
        std::cout.rdbuf(orig_cout);
        ofs.close();
        if (rc == EXIT_SUCCESS_CODE) {
            if (std::rename(tmp_path.c_str(), output_file.c_str()) != 0) {
                std::cerr << "Error: Cannot write output file: " << output_file << "\n";
                std::remove(tmp_path.c_str());
                return EXIT_INTERNAL_ERROR;
            }
        } else {
            std::remove(tmp_path.c_str());
        }
    }

    return rc;
}
