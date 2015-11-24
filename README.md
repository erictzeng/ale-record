# Cloning

Clone recursively to pull the modified version of ALE too:

```
git clone git@github.com:erictzeng/ale-record.git --recursive
```

# Installation

You may need to `brew install` and/or `pip install` a bunch of things. In
particular, `pygame` is a pain to install. Hopefully this works for you:

```
pip install hg+http://bitbucket.org/pygame/pygame
```

We also need to compile ALE with SDL:

```
cd Arcade-Learning-Environment
mkdir build
cd build
cmake .. -DUSE_SDL=on
make -j8
```

Finally, you'll need `Arcade-Learning-Environment` on your PYTHONPATH. You can
`source .envrc` in the repo root, or install the excellent
[direnv](git@github.com:direnv/direnv.git) to have it automatically modify your
path whenever you enter this directory.