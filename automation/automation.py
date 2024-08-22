import argparse
import os
import shutil
import subprocess
from enum import Enum

class Platform(Enum):
    X64 = "x64"
    WIN32 = "Win32"

class Configuration(Enum):
    Debug = "Debug"
    Release = "Release"

class Action(Enum):
    CLEAN = "clean"
    GENERATE = "generate"
    BUILD_DEBUG_EXE = "build_debug_exe"
    BUILD_RELEASE_EXE = "build_release_exe"
    BUILD_DEBUG_LIB = "build_debug_lib"
    BUILD_RELEASE_LIB = "build_release_lib"
    CLANG_FORMAT = "clang_format"

##################### manual configuration ####################

class Config:
    BUILD_FOLDER = "build"
    CMAKE_GENERATOR = "Visual Studio 17 2022" # https://cmake.org/cmake/help/latest/manual/cmake-generators.7.html
    PLATFORM = Platform.X64  # Platform.WIN32
    FRESH = True
    CLEAN = True
    VERBOSE = False
    SOURCE_DIR = "Source"
    BUILD_LIB = False
    CONFIG = Configuration.Release
    TARGET = "Stockfish"

###############################################################

FRESH_ARG = "--fresh" if Config.FRESH else ""
CLEAN_ARG = "--clean-first" if Config.CLEAN else ""
VERBOSE_ARG = "--verbose" if Config.VERBOSE else ""

def remove_build_folder():
    if os.path.exists(Config.BUILD_FOLDER):
        shutil.rmtree(Config.BUILD_FOLDER)
        print(f"Removed {Config.BUILD_FOLDER} folder.")
    else:
        print(f"{Config.BUILD_FOLDER} folder does not exist.")

def get_cmake_command(action):
    cmake_flags = {
        "generator": f'-G "{Config.CMAKE_GENERATOR}"',
        "platform": f"-A {Config.PLATFORM.value}",
        "fresh": "--fresh" if Config.FRESH else "",
        "clean_first": "--clean-first" if Config.CLEAN else "",
        "verbose": "--verbose" if Config.VERBOSE else "",
        "build_lib": f"-DBUILD_LIB={'ON' if Config.BUILD_LIB else 'OFF'}",
    }

    if action == Action.GENERATE:
        return f'cmake .. {cmake_flags["generator"]} {cmake_flags["platform"]} {cmake_flags["fresh"]} {cmake_flags["build_lib"]}'
    elif action in (Action.BUILD_DEBUG_EXE, Action.BUILD_RELEASE_EXE, Action.BUILD_DEBUG_LIB, Action.BUILD_RELEASE_LIB):
        return f'cmake --build . {cmake_flags["clean_first"]} {cmake_flags["verbose"]} --config {Config.CONFIG.value} --target {Config.TARGET}'
    return None


def run_command(command):
    result = subprocess.run(command, shell=True)
    return result.returncode == 0

def generate_project_files():
    if not os.path.exists(Config.BUILD_FOLDER):
        os.makedirs(Config.BUILD_FOLDER)
        print(f"Created {Config.BUILD_FOLDER} folder.")

    os.chdir(Config.BUILD_FOLDER)
    command = get_cmake_command(Action.GENERATE)
    print(f"Generated project files with command: {command}")

    if run_command(command):
        print("Project files generated successfully.")
    else:
        print("Failed to generate project files.")
    os.chdir("..")

def build_project(action):

    generate_project_files()

    if not os.path.exists(Config.BUILD_FOLDER):
        print(
            f"{Config.BUILD_FOLDER} folder does not exist. Please generate project files first."
        )
        return

    os.chdir(Config.BUILD_FOLDER)
    command = get_cmake_command(action)
    if run_command(command):
        print(f"Project built successfully in {Config.CONFIG} mode.")
    else:
        print(f"Failed to build project in {Config.CONFIG} mode.")
    os.chdir("..")

def get_source_files(source_dir, extensions):
    source_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                source_files.append(os.path.join(root, file))
    return source_files

def run_clang_format(source_dir):
    extensions = ['.cpp', '.h', '.hpp']
    format_sources = get_source_files(source_dir, extensions)
    
    if not format_sources:
        print(f'No source files found in {source_dir}.')
        return

    command = ['clang-format', '-i'] + format_sources
    if run_command(command):
        print('Clang-format successfully applied.')
    else:
        print('Error running clang-format.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CMake Automation Script")
    parser.add_argument(
        "action", type=Action, choices=list(Action), help="Action to perform"
    )
    args = parser.parse_args()
    
    if args.action in {Action.BUILD_DEBUG_LIB, Action.BUILD_RELEASE_LIB}:
        Config.BUILD_LIB = True
    else:
        Config.BUILD_LIB = False

    if args.action in {Action.BUILD_DEBUG_LIB, Action.BUILD_DEBUG_EXE}:
        Config.CONFIG = Configuration.Debug
    else:
        Config.CONFIG = Configuration.Release

    actions = {
        Action.CLEAN: remove_build_folder,
        Action.GENERATE: generate_project_files,
        Action.BUILD_DEBUG_EXE: lambda: build_project(Action.BUILD_DEBUG_EXE),
        Action.BUILD_RELEASE_EXE: lambda: build_project(Action.BUILD_RELEASE_EXE),
        Action.BUILD_DEBUG_LIB: lambda: build_project(Action.BUILD_DEBUG_LIB),
        Action.BUILD_RELEASE_LIB: lambda: build_project(Action.BUILD_RELEASE_LIB),
        Action.CLANG_FORMAT: lambda: run_clang_format(Config.SOURCE_DIR),
    }

    selected_action = args.action

    if selected_action in actions:
        actions[selected_action]()
    else:
        print(f"Action '{selected_action}' is not implemented.")
