import { TestBed } from '@angular/core/testing';

import { GetMapSize } from './get-map-size';

describe('GetMapSize', () => {
  let service: GetMapSize;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(GetMapSize);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
