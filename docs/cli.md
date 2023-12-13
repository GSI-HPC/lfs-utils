# lfs-utils CLI Tool

## Command

`lfsutils-cli`

## Sub-Commands

* oss - Lookup OSS by specifiying OSTs in ClusterShell [RangeSet](https://clustershell.readthedocs.io/en/latest/api/NodeSet.html) notation

* ost - Lookup OSTs by specifiying OSS in ClusterShell [NodeSet](https://clustershell.readthedocs.io/en/latest/api/RangeSet.html) notation

### oss - Lookup OSS with OST RangeSet

#### Help

```bash
./lfsutils-cli oss -h
usage: lfsutils-cli oss [-h] [-D] fsname rangeset

Lookup OSS by specifying an OST RangeSet

positional arguments:
  fsname       Filesystem name
  rangeset     RangeSet with OST decimal indexes e.g. "30-50,100-120". For hexadecimal see -x/--hex option.

options:
  -h, --help   show this help message and exit
  -D, --debug  Enable debug
  -x, --hex    Enable hexadecimal rangeset specification for OSTs e.g. "0000, 00D6-00F1, 00FF-01A0"
```

#### Example with OST decimal RangeSet

```bash
./lfsutils-cli oss fsname "30-50,100-120"
oss001.domain.de - [30, 31, 32, 33, 34]
oss003.domain.de - [35, 36, 37, 38, 39, 40, 41]
oss005.domain.de - [42, 43, 44, 45, 46, 47, 48]
oss007.domain.de - [49, 50]
oss100.domain.de - [100, 101, 102, 103, 104]
oss130.domain.de - [105, 106, 107, 108, 109, 110, 111]
oss150.domain.de - [112, 113, 114, 115, 116, 117, 118]
oss155.domain.de - [119, 120]
```

#### Example with OST hexadecimal RangeSet

```bash
./lfsutils-cli oss fsname "0000, 0010-0020,02f7-030f" -x
oss505.domain.de - [0]
oss507.domain.de - [16, 17, 18, 19, 20]
oss508.domain.de - [21, 22, 23, 24, 25, 26, 27]
oss509.domain.de - [28, 29, 30, 31, 32]
oss501.domain.de - [759, 760, 761, 762]
oss502.domain.de - [763, 764, 765, 766, 767, 768, 769]
oss503.domain.de - [770, 771, 772, 773, 774, 775, 776]
oss504.domain.de - [777, 778, 779, 780, 781, 782, 783]
```

### ost - Lookup OST with OSS NodeSet

#### Help

```bash
./lfsutils-cli ost -h
usage: lfsutils-cli ost [-h] [-D] fsname nodeset

Lookup OST by specifying an OSS NodeSet

positional arguments:
  fsname       Filesystem name
  nodeset      FQDN specified OSS as NodeSet e.g. "oss[0-9,12-20].domain"

options:
  -h, --help   show this help message and exit
  -D, --debug  Enable debug
```

#### Example

```bash
./lfsutils-cli ost fsname "oss[445-448,450].domain.de"
oss445.domain.de - [210, 211, 212, 213, 214, 215, 216]
oss446.domain.de - [217, 218, 219, 220, 221, 222, 223]
oss447.domain.de - [224, 225, 226, 227, 228, 229, 230]
oss448.domain.de - [231, 232, 233, 234, 235, 236, 237]
oss450.domain.de - [245, 246, 247, 248, 249, 250, 251]
```