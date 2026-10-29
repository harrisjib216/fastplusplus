cmake_minimum_required(VERSION 3.20)
project(fastpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

add_executable(fastpp
  src/catalog.cpp
  src/check_pii.cpp
  src/json.cpp
  src/main.cpp
  src/render.cpp
  src/seeds.cpp
  src/text.cpp)
if(NOT MSVC)
  target_compile_options(fastpp PRIVATE -Wall -Wextra -Wpedantic)
endif()
