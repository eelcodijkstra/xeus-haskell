include(FetchContent)

function(fetch_ut)
    set(UT_VERSION "v2.3.1")
    set(UT_URL "https://github.com/boost-ext/ut/archive/refs/tags/${UT_VERSION}.tar.gz")
    FetchContent_Declare(
      ut
      URL ${UT_URL}
      DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
    FetchContent_MakeAvailable(ut)
endfunction()
