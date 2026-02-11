for d in /dev/video*; do
  echo "==== $d ===="
  v4l2-ctl -d "$d" -D | sed -n '1,25p'
done
echo "randoScript ran"
