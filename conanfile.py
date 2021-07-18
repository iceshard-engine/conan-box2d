from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class Box2dConan(ConanFile):
    name = "box2d"
    license = "https://github.com/erincatto/box2d/blob/master/LICENSE"
    description = "Box2D is a 2D physics engine for games."
    url = "https://github.com/erincatto/box2d"

    # Setting and options
    settings = "os", "compiler", "arch", "build_type"
    options = { "custom_allocator_extension":[True, False] }
    default_options = {
        "custom_allocator_extension": False
    }

    # Additional files to export
    exports_sources = ["patches/*"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.7.0@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    def ice_source_key(self, version):
        if self.options.custom_allocator_extension == True:
            return "{}-alloc".format(version)
        else:
            return version

    def ice_build(self):
        self.ice_apply_patches()

        definitions = { }
        definitions['BOX2D_BUILD_DOCS'] = False
        definitions['BOX2D_BUILD_TESTBED'] = False
        definitions['BOX2D_BUILD_UNIT_TESTS'] = False
        definitions['BOX2D_USER_SETTINGS'] = False

        self.ice_run_cmake(definitions)

    def package(self):
        self.copy("LICENSE", src=self._ice.source_dir, dst="LICENSE")

        self.copy("*.h", "include/", src="{}/include".format(self._ice.source_dir), keep_path=True)

        build_dir = self._ice.build_dir
        if self.settings.os == "Windows":
            self.copy("*.lib", dst="lib", src="{}/bin".format(build_dir), keep_path=False)
            self.copy("*.pdb", dst="lib", src="{}/bin".format(build_dir), keep_path=False)
        if self.settings.os == "Linux":
            self.copy("*.a", dst="lib", src="{}/bin".format(build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = [ "lib" ]
        self.cpp_info.libs = ["box2d"]
