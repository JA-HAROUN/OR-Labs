import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';
import { MapSize } from '../models/map-size';

@Injectable({ providedIn: 'root' })
export class MapSizeService {
  private size$ = new BehaviorSubject<MapSize>({ rows: 0, columns: 0 });

  setSize(rows: number, columns: number) {
    this.size$.next({ rows: rows || 0, columns: columns || 0 });
  }

  getSize() {
    return this.size$.asObservable();
  }

  getCurrent() {
    return this.size$.value;
  }
}
