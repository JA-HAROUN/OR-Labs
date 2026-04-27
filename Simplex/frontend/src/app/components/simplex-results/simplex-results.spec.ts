import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SimplexResults } from './simplex-results';

describe('SimplexResults', () => {
  let component: SimplexResults;
  let fixture: ComponentFixture<SimplexResults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SimplexResults]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SimplexResults);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
