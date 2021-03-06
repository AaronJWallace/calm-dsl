from .package import package
from .provider_spec import read_spec
from .package import PackageType
from .validator import PropertyValidator
from .entity import Entity
from calm.dsl.tools import get_logging_handle


# Downloadable Image

# Constants
ImageType = "DISK_IMAGE"
ImageArchitecture = "X86_64"
ProductVersion = "1.0"
ConfigSections = ["image", "product", "checksum"]
LOG = get_logging_handle(__name__)


class VmDiskPackageType(PackageType):
    __schema_name__ = "VmDiskPackage"
    __openapi_type__ = "app_vm_disk_package"

    def get_ref(cls, kind=None):
        """Note: app_package kind to be used for downloadable image"""
        return super().get_ref(kind=PackageType.__openapi_type__)

    def compile(cls):
        config = super().compile()

        pkg_name = config["name"]
        pkg_doc = config["description"]

        kwargs = {
            "type": "SUBSTRATE_IMAGE",
            "options": {
                "name": config["image"].get("name") or pkg_name,
                "description": "",
                "resources": {
                    "image_type": config["image"].get("type") or ImageType,
                    "source_uri": config["image"].get("source_uri", ""),
                    "version": {
                        "product_version": config["product"].get("version")
                        or ProductVersion,
                        "product_name": config["product"].get("name") or pkg_name,
                    },
                    "architecture": config["image"].get(
                        "architecture", ImageArchitecture
                    ),
                },
            },
        }

        # If image is ISO type, search for checksum data
        if kwargs["options"]["resources"]["image_type"] == "ISO_IMAGE":
            kwargs["options"]["resources"]["checksum"] = {
                "checksum_algorithm": config["checksum"].get("algorithm", ""),
                "checksum_value": config["checksum"].get("value", ""),
            }

        pkg = package(name=pkg_name, description=pkg_doc, **kwargs)
        # return the compile version of package
        return pkg.compile()


class VmDiskPackageValidator(PropertyValidator, openapi_type="app_vm_disk_package"):
    __default__ = None
    __kind__ = VmDiskPackageType


def vm_disk_package(name="", description="", config_file=None, config={}):

    if not (config_file or config):
        raise ValueError("Downloadable image configuration not found !!!")

    if not config:
        config = read_spec(filename=config_file, depth=2)

    if not isinstance(config, dict):
        LOG.debug("Downloadable Image Config: {}".format(config))
        raise TypeError("Downloadable image configuration is not of type dict")

    config["description"] = description or config.get("description", "")
    name = name or config.get("name") or getattr(VmDiskPackageType, "__schema_name__")
    bases = (Entity,)

    # Check for given sections, if not present add an empty one
    for section in ConfigSections:
        if section not in config:
            config[section] = {}

    # Convert product version and checksum value to string
    config["product"]["version"] = str(config["product"].get("version", ""))
    config["checksum"]["value"] = str(config["checksum"].get("value", ""))

    return VmDiskPackageType(name, bases, config)


def ahv_vm_disk_package(name="", description="", config_file=None, config_data={}):

    if not (config_file or config_data):
        raise ValueError("Downloadable image configuration not found !!!")

    if not config_data:
        config_data = read_spec(filename=config_file, depth=2)

    if not isinstance(config_data, dict):
        LOG.debug("Downloadable Image Config: {}".format(config_data))
        raise TypeError("Downloadable image configuration is not of type dict")

    return vm_disk_package(name=name, description=description, config=config_data)
