cmake_minimum_required(VERSION 3.30)

set(PROJECT_NAME Stockfish)
project(${PROJECT_NAME})

# common options
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set_property(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR} PROPERTY VS_STARTUP_PROJECT ${PROJECT_NAME})

set(SRCS 
    src/benchmark.cpp src/bitboard.cpp src/evaluate.cpp
    src/misc.cpp src/movegen.cpp src/movepick.cpp src/position.cpp
    src/search.cpp src/thread.cpp src/timeman.cpp src/tt.cpp src/uci.cpp src/ucioption.cpp src/tune.cpp src/syzygy/tbprobe.cpp
    src/nnue/nnue_misc.cpp src/nnue/features/half_ka_v2_hm.cpp src/nnue/network.cpp src/engine.cpp src/score.cpp src/memory.cpp
)

set(HEADERS
    src/benchmark.h src/bitboard.h src/evaluate.h src/misc.h src/movegen.h src/movepick.h
    src/nnue/nnue_misc.h src/nnue/features/half_ka_v2_hm.h src/nnue/layers/affine_transform.h
    src/nnue/layers/affine_transform_sparse_input.h src/nnue/layers/clipped_relu.h src/nnue/layers/simd.h
    src/nnue/layers/sqr_clipped_relu.h src/nnue/nnue_accumulator.h src/nnue/nnue_architecture.h
    src/nnue/nnue_common.h src/nnue/nnue_feature_transformer.h src/position.h
    src/search.h src/syzygy/tbprobe.h src/thread.h src/thread_win32_osx.h src/timeman.h
    src/tt.h src/tune.h src/types.h src/uci.h src/ucioption.h src/perft.h src/nnue/network.h src/engine.h src/score.h src/numa.h src/memory.h
)

# Include directories
include_directories(syzygy nnue nnue/features)

# Compiler and Linker Flags
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")

add_compile_definitions(_ITERATOR_DEBUG_LEVEL=0)

# Add the executable
option(BUILD_LIB "Build lib or exe" OFF)
if(BUILD_LIB)
    add_library(${PROJECT_NAME} STATIC ${SRCS} ${HEADERS})
else()
    add_executable(${PROJECT_NAME} ${SRCS} src/main.cpp ${HEADERS})
endif()
