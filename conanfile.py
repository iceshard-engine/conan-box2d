from conans import ConanFile, MSBuild, tools
from shutil import copyfile
import os

class Box2dConan(ConanFile):
    name = "box2d"
    license = "https://github.com/erincatto/box2d/blob/master/LICENSE"
    description = "Box2D is a 2D physics engine for games."
    url = "https://github.com/erincatto/box2d"

    # Setting and options
    settings = "os", "compiler", "arch"
    options = { "custom_allocator_extension":[True, False] }
    default_options = {
        "custom_allocator_extension": False
    }

    # Additional files to export
    exports_sources = ["patches/*"]

    # Iceshard conan tools
    python_requires = "conan-iceshard-tools/0.6.4@iceshard/stable"
    python_requires_extend = "conan-iceshard-tools.IceTools"

    def init(self):
        self.ice_init("cmake")
        self.build_requires = self._ice.build_requires

    # Override the source entry method
    def ice_source_entry(self, version):
        # We are appending '-docking' string so the right entry from 'conandata.yml' file is picked.
        if self.options.custom_allocator_extension == True:
            return "{}-alloc".format(version)
        else:
            return version

    # Build both the debug and release builds
    def ice_build(self):
        self.ice_apply_patches()

        definitions = { }
        definitions['BOX2D_BUILD_DOCS'] = False
        definitions['BOX2D_BUILD_TESTBED'] = False
        definitions['BOX2D_BUILD_UNIT_TESTS'] = False
        definitions['BOX2D_USER_SETTINGS'] = False

        self.ice_build_cmake(["Debug", "Release"], definitions)

    def package(self):
        self.copy("LICENSE", src=self._ice.out_dir, dst="LICENSE")

        self.copy("*.h", "include/", src="{}/include".format(self._ice.out_dir), keep_path=True)

        for config in ["Debug", "Release"]:
            build_dir = os.path.join(self._ice.out_dir, "../build_{}/".format(config))

            if self.settings.os == "Windows":
                self.copy("*.lib", dst="lib/{}".format(config), src="{}/bin".format(build_dir), keep_path=False)
                self.copy("*.pdb", dst="lib/{}".format(config), src="{}/bin".format(build_dir), keep_path=False)
            if self.settings.os == "Linux":
                self.copy("*.a", dst="lib/{}".format(config), src="{}/bin".format(build_dir), keep_path=False)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.debug.libdirs = [ "lib/Debug" ]
        self.cpp_info.release.libdirs = [ "lib/Release" ]
        self.cpp_info.libs = ["box2d"]
