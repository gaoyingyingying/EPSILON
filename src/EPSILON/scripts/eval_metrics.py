#!/usr/bin/env python3
import argparse
import json
import math
import signal
import sys
import time

import rospy
from vehicle_msgs.msg import ArenaInfoDynamic


class MetricCollector:
    def __init__(self, ego_id, safety_distance, ud_threshold, lcc_threshold):
        self.ego_id = ego_id
        self.safety_distance = safety_distance
        self.ud_threshold = ud_threshold
        self.lcc_threshold = lcc_threshold

        self.frames = 0
        self.unsafe_frames = 0
        self.velocity_sum = 0.0

        self.total_distance_m = 0.0
        self.ud_count = 0
        self.lcc_count = 0

        self.prev_stamp = None
        self.prev_pos = None
        self.prev_curvature = None
        self.prev_ud_active = False
        self.prev_lcc_active = False

    def _find_ego(self, vehicles):
        for v in vehicles:
            if v.id.data == self.ego_id:
                return v
        return None

    def callback(self, msg):
        vehicles = msg.vehicle_set.vehicles
        ego = self._find_ego(vehicles)
        if ego is None:
            return

        self.frames += 1
        ex = ego.state.vec_position.x
        ey = ego.state.vec_position.y
        ev = ego.state.velocity
        ea = ego.state.acceleration
        ek = ego.state.curvature

        self.velocity_sum += ev

        min_dist = float("inf")
        for v in vehicles:
            if v.id.data == self.ego_id:
                continue
            dx = ex - v.state.vec_position.x
            dy = ey - v.state.vec_position.y
            d = math.hypot(dx, dy)
            if d < min_dist:
                min_dist = d

        if min_dist < self.safety_distance:
            self.unsafe_frames += 1

        stamp = msg.header.stamp.to_sec()
        if self.prev_pos is not None:
            self.total_distance_m += math.hypot(ex - self.prev_pos[0], ey - self.prev_pos[1])

        dt = None
        if self.prev_stamp is not None:
            dt = stamp - self.prev_stamp

        ud_active = ea < -self.ud_threshold
        if ud_active and not self.prev_ud_active:
            self.ud_count += 1
        self.prev_ud_active = ud_active

        lcc_active = False
        if dt is not None and dt > 1e-6 and self.prev_curvature is not None:
            curvature_change_rate = abs((ek - self.prev_curvature) / dt)
            lcc_active = curvature_change_rate > self.lcc_threshold
        if lcc_active and not self.prev_lcc_active:
            self.lcc_count += 1
        self.prev_lcc_active = lcc_active

        self.prev_stamp = stamp
        self.prev_pos = (ex, ey)
        self.prev_curvature = ek

    def summarize(self):
        avg_vel = self.velocity_sum / self.frames if self.frames else 0.0
        unsafe_ratio = self.unsafe_frames / self.frames if self.frames else 0.0
        distance_km = self.total_distance_m / 1000.0
        norm = distance_km if distance_km > 1e-9 else 1e-9

        return {
            "frames": self.frames,
            "unsafe_frames": self.unsafe_frames,
            "unsafe_ratio": unsafe_ratio,
            "average_velocity_mps": avg_vel,
            "distance_m": self.total_distance_m,
            "ud_count": self.ud_count,
            "lcc_count": self.lcc_count,
            "ud_per_km": self.ud_count / norm,
            "lcc_per_km": self.lcc_count / norm,
            "safety_distance_m": self.safety_distance,
            "ud_threshold_mps2": self.ud_threshold,
            "lcc_threshold_inv_sm": self.lcc_threshold,
        }


def main():
    parser = argparse.ArgumentParser(description="Collect EUDM/MPDM metrics from /arena_info_dynamic")
    parser.add_argument("--ego-id", type=int, default=0)
    parser.add_argument("--topic", default="/arena_info_dynamic")
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--safety-distance", type=float, default=5.0)
    parser.add_argument("--ud-threshold", type=float, default=1.6)
    parser.add_argument("--lcc-threshold", type=float, default=0.12)
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    rospy.init_node("epsilon_metric_collector", anonymous=True)
    collector = MetricCollector(
        ego_id=args.ego_id,
        safety_distance=args.safety_distance,
        ud_threshold=args.ud_threshold,
        lcc_threshold=args.lcc_threshold,
    )

    rospy.Subscriber(args.topic, ArenaInfoDynamic, collector.callback, queue_size=100)

    stop = False

    def _handle_sigint(_sig, _frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, _handle_sigint)

    start = time.time()
    rate = rospy.Rate(50)
    while not rospy.is_shutdown() and not stop and (time.time() - start) < args.duration:
        rate.sleep()

    result = collector.summarize()
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
