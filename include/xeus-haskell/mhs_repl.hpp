#pragma once
#include <expected>
#include <string>
#include <string_view>
#include "Repl_stub.h"

namespace xeus_haskell {

class MicroHsRepl {
public:
    MicroHsRepl(); // calls mhs_init() and mhs_repl_new()
    ~MicroHsRepl(); // calls mhs_repl_free()

    std::expected<std::string, std::string> execute(std::string_view code);

private:
    uintptr_t context = 0;
};

} // namespace xeus_haskell
