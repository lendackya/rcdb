#(!) this CMake build system IS experimental and is made mostly for using CLion IDE.
# Scons - is the main RCDB make system, so please use it in order to build rcdb.lib and examples

cmake_minimum_required(VERSION 3.4)
project(rcdb_cpp)


# Location of additional CMake modules
SET(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} "${CMAKE_SOURCE_DIR}/cmake/")

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")


include_directories(include)
include_directories(include/SQLite)
include_directories(/usr/include/mysql)

set(SOURCE_FILES
        src/SQLite/sqlite3.c
        src/SQLiteCpp/Backup.cpp
        src/SQLiteCpp/Column.cpp
        src/SQLiteCpp/Database.cpp
        src/SQLiteCpp/Statement.cpp
        src/SQLiteCpp/Transaction.cpp

        include/RCDB/ConditionType.h
        include/RCDB/MySqlProvider.h
        include/RCDB/SqLiteProvider.h
        include/RCDB/DataProvider.h
        include/RCDB/Condition.h
        include/RCDB/Exceptions.h
        include/RCDB/MySqlConnectionInfo.h
        include/RCDB/Connection.h
        include/RCDB/StringUtils.h
        include/RCDB/ConfigParser.h
        include/RCDB/RcdbFile.h
        )

SET(EXAMPLES_SOURCE_FILES
        ${SOURCE_FILES}
        #examples/simple.cpp
        examples/get_trigger_params.cpp
        )

SET(TEST_SOURCE_FILES
        ${SOURCE_FILES}

        include/RCDB/ConditionType.h
        include/RCDB/MySqlProvider.h
        include/RCDB/SqLiteProvider.h
        include/RCDB/DataProvider.h
        include/RCDB/Condition.h
        include/RCDB/Exceptions.h
        include/RCDB/MySqlConnectionInfo.h
        include/RCDB/Connection.h
        include/RCDB/StringUtils.h
        include/RCDB/ConfigParser.h

        tests/test_Connection.cpp
        tests/test_ConditionType.cpp
        tests/test_MySqlProvider.cpp
        tests/test_SqLiteProvider.cpp

        tests/catch.hpp
        tests/catch.cpp
        tests/test_ConfigParser.cpp)




add_executable(test_rcdb_cpp ${TEST_SOURCE_FILES} )
add_executable(examples_rcdb_cpp ${EXAMPLES_SOURCE_FILES} )

target_link_libraries(test_rcdb_cpp mysqlclient dl pthread)
target_link_libraries(examples_rcdb_cpp mysqlclient dl pthread)