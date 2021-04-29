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
    python_requires = "conan-iceshard-tools/0.6.2@iceshard/stable"
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
        # Apply patches if existing
        patch_info = self.conan_data["patches"].get(self.ice_source_entry(self.version))
        if patch_info != None:
            for patch in patch_info:
                tools.patch(patch_file="../{}".format(patch["patch_file"]))

        self.ice_build_cmake(["Debug", "Release"])

    def package(self):
        self.copy("LICENSE", src=self._ice.out_dir, dst="LICENSE")

        self.copy("*.h", "include/", src="{}/include".format(self._ice.out_dir), keep_path=True)

        for config in ["Debug", "Release"]:
            build_dir = os.path.join(self._ice.out_dir, "build/bin/{}".format(config))
            if self.settings.os == "Windows":
                self.copy("box2d.lib", "lib/{}".format(config), build_dir, keep_path=True)
            if self.settings.os == "Linux":
                self.copy("box2d.a", "lib/{}".format(config), build_dir, keep_path=True)

    def package_info(self):
        self.cpp_info.libdirs = []
        self.cpp_info.debug.libdirs = [ "lib/Debug" ]
        self.cpp_info.release.libdirs = [ "lib/Release" ]
        self.cpp_info.libs = ["box2d"]
