#!/bin/bash -e

run() {
	printf "$ $ANSI_YELLOW%s$ANSI_CLEAR\n" "$(echo $@)" >&2
	"$@"
}

remote_url="$(git remote get-url origin)"
pages_dir="$TRAVIS_BUILD_DIR-gh-pages"

echo 'Write GITHUB_ACCESS_TOKEN to ~/.netrc'
cat > ~/.netrc << EOF
machine github.com
  login $GITHUB_ACCESS_TOKEN
EOF

run git clone --depth=1 --no-single-branch --branch=gh-pages "$remote_url" "$pages_dir"
run cd "$pages_dir"

run find . -name .is_ref | while read line; do
	ref="$(dirname "$line")"
	ref="${ref:2}"
	if ! git rev-parse --verify -q "refs/remotes/origin/$ref" > /dev/null; then
		run rm -rf "$ref"
	fi
done

run git status

run cd "$TRAVIS_BUILD_DIR"
run docker run --rm -i -v "$TRAVIS_BUILD_DIR:/app" -w /app mgjm/sn3t:base << EOF
apt-get update
apt-get install -y make graphviz

pip3 install -r docs/requirements.txt

ln -s /app/testbed "\$PYTHONPATH/testbed"

export VERSIONS_JS_URL=https://osmhpi.github.io/cohydra/versions.js

export SUMO_HOME=
exec make docs BUILD_TAG="$TRAVIS_BRANCH"
EOF

run rm -rf "$pages_dir/${TRAVIS_BRANCH}"
run mkdir -pv "$pages_dir/${TRAVIS_BRANCH}"
run cp -Trv docs/build/dirhtml "$pages_dir/${TRAVIS_BRANCH}"
run touch "$pages_dir/${TRAVIS_BRANCH}/.is_ref"

run cd "$pages_dir"
run .travis-scripts/build_versions.py

if [ -z "$(git status --porcelain)" ]; then
	echo "Nothing to commit"
else
	run git add .
	run git commit -m "Build docs for ${TRAVIS_COMMIT::7} on branch ${TRAVIS_BRANCH}"
	run git push
fi
