// Copyright 2026 Mark Alan Boykin
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at https://mozilla.org/MPL/2.0/.
// SPDX-License-Identifier: MPL-2.0

use std::sync::Mutex;

/// Status-only capture callbacks must not evict an unconsumed image. Keep
/// custody bounded to one image, replacing it only when a newer image arrives.
pub(crate) fn update_latest_image<T>(latest: &Mutex<Option<T>>, image: Option<T>) {
    if let Ok(mut slot) = latest.lock() {
        *slot = image;
    }
}

#[cfg(test)]
mod tests {
    use super::update_latest_image;
    use std::sync::atomic::{AtomicUsize, Ordering};
    use std::sync::{Arc, Mutex};

    struct Image {
        id: usize,
        drops: Arc<AtomicUsize>,
    }

    impl Drop for Image {
        fn drop(&mut self) {
            self.drops.fetch_add(1, Ordering::Relaxed);
        }
    }

    #[test]
    fn status_only_burst_preserves_pending_image_and_its_custody() {
        let drops = Arc::new(AtomicUsize::new(0));
        let latest = Mutex::new(None);
        update_latest_image(
            &latest,
            Some(Image {
                id: 1,
                drops: drops.clone(),
            }),
        );
        for _ in 0..100 {
            update_latest_image(&latest, None);
        }
        assert_eq!(drops.load(Ordering::Relaxed), 0);
        let image = latest.lock().unwrap().take().unwrap();
        assert_eq!(image.id, 1);
        assert!(latest.lock().unwrap().is_none());
        drop(image);
        assert_eq!(drops.load(Ordering::Relaxed), 1);
    }

    #[test]
    fn newer_image_replaces_only_one_pending_image() {
        let drops = Arc::new(AtomicUsize::new(0));
        let latest = Mutex::new(None);
        for id in 1..=2 {
            update_latest_image(
                &latest,
                Some(Image {
                    id,
                    drops: drops.clone(),
                }),
            );
        }
        assert_eq!(drops.load(Ordering::Relaxed), 1);
        let image = latest.lock().unwrap().take().unwrap();
        assert_eq!(image.id, 2);
        drop(image);
        assert_eq!(drops.load(Ordering::Relaxed), 2);
    }
}
