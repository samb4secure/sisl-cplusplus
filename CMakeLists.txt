cmake_minimum_required(VERSION 3.14)
project(sislc VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

include(FetchContent)

FetchContent_Declare(
    json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG v3.11.3
)
FetchContent_MakeAvailable(json)

add_executable(sislc
    src/main.cpp
    src/sisl_lexer.cpp
    src/sisl_parser.cpp
    src/sisl_codec.cpp
    src/merge.cpp
    src/split.cpp
    src/unicode_escape.cpp
)

target_include_directories(sislc PRIVATE src)
target_link_libraries(sislc PRIVATE nlohmann_json::nlohmann_json)

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(sislc PRIVATE -Wall -Wextra -Wpedantic)
endif()

install(TARGETS sislc RUNTIME DESTINATION bin)
