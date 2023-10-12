# lfs-utils CLI Tool

## Command

`lfsutils-cli`

## Sub-Commands

* oss - Lookup OSS with NodeSet
* ost - Lookup OST with RangeSet

### oss - Lookup OSS with NodeSet

#### Help

```bash
./lfsutils-cli oss -h
usage: lfsutils-cli oss [-h] [-D] fsname rangeset

Lookup OSS by specifying an OST RangeSet

positional arguments:
  fsname       Filesystem name
  rangeset     RangeSet with OST indexes e.g. "30-50,100-120"

options:
  -h, --help   show this help message and exit
  -D, --debug  Enable debug
```

#### Example

```bash
./lfsutils-cli oss hebe "30-50,100-120"
oss001.domain.de - [30, 31, 32, 33, 34]
oss003.domain.de - [35, 36, 37, 38, 39, 40, 41]
oss005.domain.de - [42, 43, 44, 45, 46, 47, 48]
oss007.domain.de - [49, 50]
oss100.domain.de - [100, 101, 102, 103, 104]
oss130.domain.de - [105, 106, 107, 108, 109, 110, 111]
oss150.domain.de - [112, 113, 114, 115, 116, 117, 118]
oss155.domain.de - [119, 120]
```

### ost - Lookup OST with RangeSet

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
./lfsutils-cli ost hebe "oss[445-448,450].domain.de"
oss445.domain.de - [210, 211, 212, 213, 214, 215, 216]
oss446.domain.de - [217, 218, 219, 220, 221, 222, 223]
oss447.domain.de - [224, 225, 226, 227, 228, 229, 230]
oss448.domain.de - [231, 232, 233, 234, 235, 236, 237]
oss450.domain.de - [245, 246, 247, 248, 249, 250, 251]
```