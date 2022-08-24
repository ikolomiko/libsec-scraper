#!/usr/bin/env bash

# Usage: ./ivy-wrapper.sh <library id>
set -e

SECONDS=0
IVY_ROOT="$(dirname $(realpath "$0"))"
JAVA_BIN="/usr/bin/java"
IVY_BIN="$IVY_ROOT/ivy-2.5.0.jar"
IVY_SETTINGS="$IVY_ROOT/ivysettings.xml"
DEPS_DIR=$(mktemp -d)
LIB_ID=$1
IFS=+ read -r GROUPID ARTIFACTID VERSION <<< $LIB_ID

run_ivy() {
    $JAVA_BIN -jar $IVY_BIN -dependency $GROUPID $ARTIFACTID $VERSION -retrieve "$DEPS_DIR/[organization]+[artifact]+[revision](+[classifier]).[ext]" -settings $IVY_SETTINGS -cache cachedir
}

IVY_OUT=$(run_ivy | tee /dev/tty)
# Stop running once the desired output is displayed or the file has been downloaded

#run_ivy
#echo $IVY_OUT | tail
EXT=$(echo $IVY_OUT | sed "s/.*$GROUPID#$ARTIFACTID;$VERSION in //" | sed "s/ .*//" | sed "s/.*-//")
echo $EXT
[[ ! $EXT =~ ^(aar|jar)$ ]] && EXT="jar"

DEST="$IVY_ROOT/libs/$GROUPID+$ARTIFACTID"
mkdir -p $DEST
JAR="$DEPS_DIR/$LIB_ID.jar"
AAR="$DEPS_DIR/$LIB_ID.aar"

if [ -f $JAR ]; then
    cp $JAR "$DEST/$VERSION.$EXT"
elif [ -f $AAR ]; then
    cp $AAR "$DEST/$VERSION.aar"
fi

echo $DEPS_DIR
#rm -r $DEPS_DIR
echo "Done in $SECONDS seconds"
exit 0